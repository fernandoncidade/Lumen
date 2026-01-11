from PySide6.QtCore import QThread, Signal
from source.utils.LogManager import LogManager
import edge_tts
from edge_tts.exceptions import NoAudioReceived
import asyncio
import os
import re
import uuid
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente


class WordTimestamp:
    def __init__(self, text: str, offset_ms: int, duration_ms: int, text_offset: int = 0):
        self.text = text
        self.offset_ms = offset_ms
        self.duration_ms = duration_ms
        self.text_offset = text_offset

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "offset_ms": self.offset_ms,
            "duration_ms": self.duration_ms,
            "text_offset": self.text_offset
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WordTimestamp":
        return cls(
            text=d.get("text", ""),
            offset_ms=d.get("offset_ms", 0),
            duration_ms=d.get("duration_ms", 0),
            text_offset=d.get("text_offset", 0)
        )


class EdgeTTSWithTimestamps(QThread):
    chunk_ready = Signal(str, list)
    error = Signal(str)
    word_timestamps_ready = Signal(list)

    def __init__(self, texto: str, voz: str = "pt-BR-AntonioNeural", rate_pct: int = 0, volume_pct: int = 0, outdir: str = None):
        super().__init__()
        self.logger = LogManager.get_logger()
        self.texto = texto
        self.voz = voz
        self.rate_pct = rate_pct
        self.volume_pct = volume_pct
        self.outdir = outdir or obter_caminho_persistente()

        try:
            os.makedirs(self.outdir, exist_ok=True)

        except Exception:
            pass

        self._should_stop = False
        self._is_running = False
        self._active_loop = None
        self._current_comm = None
        self._current_gen = None
        self._tracking_comms = set()
        self._current_outfile_part = None
        self._all_timestamps = []

    def stop(self):
        try:
            self._should_stop = True

            try:
                p = getattr(self, "_current_outfile_part", None)
                if p and os.path.exists(p):
                    try:
                        os.remove(p)

                    except Exception:
                        pass

            except Exception:
                pass

            try:
                loop = self._active_loop
                if loop is None:
                    return

                async def _force_shutdown():
                    try:
                        current = asyncio.current_task()
                        tasks = [t for t in asyncio.all_tasks() if t is not current and not t.done()]
                        for t in tasks:
                            try:
                                t.cancel()

                            except Exception:
                                pass

                        if tasks:
                            await asyncio.gather(*tasks, return_exceptions=True)

                    except Exception:
                        pass

                    try:
                        gen = getattr(self, "_current_gen", None)
                        if gen is not None:
                            aclose = getattr(gen, "aclose", None)
                            if aclose:
                                try:
                                    await aclose()

                                except Exception:
                                    pass

                    except Exception:
                        pass

                    try:
                        comm = getattr(self, "_current_comm", None)
                        comms = list(self._tracking_comms) if self._tracking_comms else []
                        if comm is not None and comm not in comms:
                            comms.append(comm)

                        for c in comms:
                            try:
                                aclose_comm = getattr(c, "aclose", None)
                                if aclose_comm:
                                    try:
                                        await aclose_comm()

                                    except Exception:
                                        pass

                                else:
                                    sess = getattr(c, "_session", None) or getattr(c, "session", None)
                                    if sess is not None:
                                        close_fn = getattr(sess, "close", None)
                                        if asyncio.iscoroutinefunction(close_fn):
                                            try:
                                                await close_fn()

                                            except Exception:
                                                pass

                                        elif callable(close_fn):
                                            try:
                                                close_fn()

                                            except Exception:
                                                pass

                            except Exception:
                                pass

                    except Exception:
                        pass

                try:
                    fut = asyncio.run_coroutine_threadsafe(_force_shutdown(), loop)
                    try:
                        fut.result(timeout=2.0)

                    except Exception:
                        pass

                except Exception:
                    pass

            except Exception as e:
                self.logger.debug(f"Erro ao agendar fechamento de recursos assíncronos: {e}", exc_info=True)

        except Exception as e:
            self.logger.error(f"Erro ao solicitar parada da thread: {e}", exc_info=True)

    def _split_text(self, text: str, max_chars: int = 3500) -> list:
        sentences = re.split(r'(?<=[\.\?\!\n])\s+', text)
        chunks = []
        cur = ""
        for s in sentences:
            s = s.strip()
            if not s:
                continue

            if len(cur) + len(s) + 1 <= max_chars:
                cur = (cur + " " + s).strip() if cur else s

            else:
                if cur:
                    chunks.append(cur)

                cur = s

        if cur:
            chunks.append(cur)

        return chunks

    def _normalize_voice(self, voz: str) -> str:
        try:
            if not voz:
                return voz

            if re.match(r'^[a-z]{2}-[A-Z]{2}-', voz):
                return voz

            m = re.search(r'\(\s*(?P<locale>[a-z]{2}-[A-Z]{2})\s*,\s*(?P<token>[A-Za-z0-9_ -]+)\s*\)', voz)
            if m:
                token = m.group('token').strip().replace(' ', '')
                return f"{m.group('locale')}-{token}"

            m2 = re.search(r'([a-z]{2}-[A-Z]{2}-[A-Za-z0-9_]+)', voz)
            if m2:
                return m2.group(1)

            m3 = re.search(r'([a-z]{2}-[A-Z]{2})\s*,\s*([A-Za-z0-9_ -]+)', voz)
            if m3:
                token = m3.group(2).strip().replace(' ', '')
                return f"{m3.group(1)}-{token}"

            self.logger.debug(f"Voice id '{voz}' parece inválido; normalizando com 'pt-BR-' prefix.")
            return f"pt-BR-{voz}"

        except Exception as e:
            self.logger.error(f"Erro ao normalizar voz: {e}", exc_info=True)

        return voz

    def _calculate_text_offset(self, word: str, segment: str, last_offset: int) -> int:
        try:
            idx = segment.lower().find(word.lower(), last_offset)
            if idx >= 0:
                return idx

            idx = segment.lower().find(word.lower())
            if idx >= 0:
                return idx

        except Exception:
            pass

        return last_offset

    def _find_word_in_full_text(self, word: str, full_text: str, start: int) -> tuple[int, int, int]:
        try:
            if start is None or start < 0:
                start = 0

            w = (word or "").strip()
            if not w:
                return -1, start, 0

            def _norm(s: str) -> str:
                return (
                    (s or "")
                    .replace("’", "'")
                    .replace("‘", "'")
                    .replace("`", "'")
                    .replace("´", "'")
                )

            full_norm = _norm(full_text)
            w_norm = _norm(w)
            full_lower = full_norm.lower()
            w_lower = w_norm.lower()

            candidates: list[tuple[str, int]] = [(w_lower, len(w_lower))]
            try:
                stripped = re.sub(r"^\W+|\W+$", "", w_lower, flags=re.UNICODE)
                if stripped and stripped != w_lower:
                    candidates.insert(0, (stripped, len(stripped)))
            except Exception:
                pass

            for cand, clen in candidates:
                pos = full_lower.find(cand, start)
                if pos >= 0:
                    return pos, pos + clen, clen

            for cand, clen in candidates:
                pos = full_lower.find(cand)
                if pos >= 0:
                    return pos, pos + clen, clen

        except Exception:
            pass

        return -1, start, 0

    def run(self):
        try:
            self._is_running = True
            chunks = self._split_text(self.texto)
            fallback_voices = ["pt-BR-AntonioNeural", "en-US-JennyNeural"]

            loop = asyncio.new_event_loop()
            self._active_loop = loop

            global_text_cursor = 0

            try:
                asyncio.set_event_loop(loop)

                async def synth_all():
                    nonlocal global_text_cursor

                    for idx, seg in enumerate(chunks):
                        if self._should_stop:
                            self.logger.debug("EdgeTTSWithTimestamps: parada solicitada.")
                            return

                        uid = uuid.uuid4().hex
                        outfile = os.path.join(self.outdir, f"tts_edge_ts_{os.getpid()}_{uid}_{idx}.mp3")
                        outfile_part = outfile + ".part"
                        self._current_outfile_part = outfile_part

                        tried = []
                        candidates = []
                        if self.voz:
                            candidates.append(self.voz)
                            candidates.append(self._normalize_voice(self.voz))

                        for fv in fallback_voices:
                            if fv not in candidates:
                                candidates.append(fv)

                        success = False
                        last_err = None
                        chunk_timestamps = []

                        for voice_candidate in candidates:
                            if not voice_candidate or voice_candidate in tried:
                                continue

                            tried.append(voice_candidate)
                            comm = None
                            gen = None
                            outfile_handle = None
                            chunk_timestamps = []
                            last_word_offset = 0
                            trial_text_cursor = global_text_cursor

                            try:
                                comm = edge_tts.Communicate(
                                    seg, 
                                    voice=voice_candidate, 
                                    rate=f"{self.rate_pct:+d}%", 
                                    volume=f"{self.volume_pct:+d}%",
                                    boundary="WordBoundary"
                                )
                                self._current_comm = comm

                                try:
                                    self._tracking_comms.add(comm)

                                except Exception:
                                    pass

                                gen = comm.stream()
                                self._current_gen = gen

                                outfile_handle = open(outfile_part, "wb")

                                try:
                                    async for chunk in gen:
                                        if self._should_stop:
                                            self.logger.debug("Parada solicitada durante stream.")
                                            break

                                        chunk_type = chunk.get("type")

                                        if chunk_type == "audio":
                                            outfile_handle.write(chunk.get("data", b""))
                                            outfile_handle.flush()

                                        elif chunk_type == "WordBoundary":
                                            try:
                                                word_text = chunk.get("text", "")
                                                offset_ticks = chunk.get("offset", 0)
                                                duration_ticks = chunk.get("duration", 0)

                                                offset_ms = offset_ticks // 10000
                                                duration_ms = duration_ticks // 10000

                                                absolute_text_pos, next_cursor, matched_len = self._find_word_in_full_text(
                                                    word_text,
                                                    self.texto,
                                                    trial_text_cursor,
                                                )

                                                if absolute_text_pos >= 0:
                                                    trial_text_cursor = next_cursor

                                                    try:
                                                        if matched_len > 0:
                                                            word_text_for_ts = self.texto[absolute_text_pos:absolute_text_pos + matched_len]

                                                        else:
                                                            word_text_for_ts = word_text

                                                    except Exception:
                                                        word_text_for_ts = word_text

                                                else:
                                                    text_pos = self._calculate_text_offset(word_text, seg, last_word_offset)
                                                    last_word_offset = text_pos + len(word_text)
                                                    absolute_text_pos = max(0, global_text_cursor)
                                                    word_text_for_ts = word_text

                                                wt = WordTimestamp(
                                                    text=word_text_for_ts,
                                                    offset_ms=offset_ms,
                                                    duration_ms=duration_ms,
                                                    text_offset=absolute_text_pos
                                                )
                                                chunk_timestamps.append(wt)

                                            except Exception as e:
                                                self.logger.debug(
                                                    f"Erro ao processar WordBoundary: {e}", 
                                                    exc_info=True
                                                )

                                except asyncio.CancelledError:
                                    self.logger.debug("EdgeTTSWithTimestamps: stream cancelado.")
                                    if os.path.exists(outfile_part):
                                        try:
                                            os.remove(outfile_part)

                                        except Exception:
                                            pass

                                    return

                                if self._should_stop:
                                    self.logger.debug("EdgeTTSWithTimestamps: geração interrompida.")
                                    return

                                success = True
                                global_text_cursor = trial_text_cursor

                            except NoAudioReceived as nae:
                                last_err = str(nae)
                                self.logger.warning(f"No audio recebido com voice='{voice_candidate}': {nae}")

                            except Exception as e:
                                last_err = str(e)
                                self.logger.error(
                                    f"Erro ao sintetizar segmento {idx} com voice '{voice_candidate}': {e}", 
                                    exc_info=True
                                )

                            finally:
                                try:
                                    if outfile_handle:
                                        outfile_handle.close()

                                except Exception:
                                    pass

                                try:
                                    if gen is not None:
                                        aclose = getattr(gen, "aclose", None)
                                        if aclose:
                                            await aclose()

                                except Exception:
                                    pass

                                try:
                                    if comm is not None:
                                        aclose_comm = getattr(comm, "aclose", None)
                                        if aclose_comm:
                                            await aclose_comm()

                                        else:
                                            close_comm = getattr(comm, "close", None)
                                            if close_comm:
                                                try:
                                                    close_comm()

                                                except Exception:
                                                    pass

                                except Exception:
                                    pass

                                self._current_gen = None
                                self._current_comm = None
                                try:
                                    if comm in self._tracking_comms:
                                        self._tracking_comms.discard(comm)

                                except Exception:
                                    pass

                            if not success:
                                try:
                                    if os.path.exists(outfile_part):
                                        os.remove(outfile_part)

                                except Exception:
                                    pass

                                continue

                            if success:
                                try:
                                    try:
                                        os.replace(outfile_part, outfile)

                                    except Exception:
                                        os.rename(outfile_part, outfile)

                                except Exception:
                                    self.logger.error(
                                        f"Falha ao renomear arquivo TTS: {outfile_part} -> {outfile}", 
                                        exc_info=True
                                    )

                                self.logger.debug(
                                    f"Síntese OK: voz={voice_candidate} segmento={idx} "
                                    f"arquivo={outfile} timestamps={len(chunk_timestamps)}"
                                )

                                self._all_timestamps.extend(chunk_timestamps)
                                timestamps_dicts = [wt.to_dict() for wt in chunk_timestamps]
                                self.chunk_ready.emit(outfile, timestamps_dicts)
                                self.word_timestamps_ready.emit(timestamps_dicts)

                                break

                        if not success:
                            msg = last_err or "Falha desconhecida ao sintetizar áudio"
                            self.logger.error(f"Erro ao sintetizar segmento {idx}: {msg}", exc_info=True)
                            self.error.emit(msg)
                            return

                try:
                    loop.run_until_complete(synth_all())

                except asyncio.CancelledError:
                    self.logger.debug("EdgeTTSWithTimestamps: run interrupted by CancelledError.")

                except Exception:
                    raise

            finally:
                try:
                    loop.run_until_complete(loop.shutdown_asyncgens())

                except Exception:
                    pass

                try:
                    for c in list(self._tracking_comms):
                        try:
                            aclose_comm = getattr(c, "aclose", None)
                            if aclose_comm:
                                loop.run_until_complete(aclose_comm())

                            else:
                                sess = getattr(c, "_session", None) or getattr(c, "session", None)
                                if sess is not None:
                                    close_fn = getattr(sess, "close", None)
                                    if asyncio.iscoroutinefunction(close_fn):
                                        loop.run_until_complete(close_fn())

                                    elif callable(close_fn):
                                        close_fn()

                        except Exception:
                            pass

                except Exception:
                    pass

                try:
                    asyncio.set_event_loop(None)

                except Exception:
                    pass

                try:
                    loop.close()

                except Exception:
                    pass

                self._active_loop = None

            self._is_running = False
            return

        except Exception as e:
            self.logger.error(f"Erro ao executar Edge TTS com timestamps: {str(e)}", exc_info=True)
            self.error.emit(str(e))

        finally:
            self._is_running = False
            try:
                if self._active_loop:
                    try:
                        self._active_loop.run_until_complete(self._active_loop.shutdown_asyncgens())

                    except Exception:
                        pass

                    try:
                        self._active_loop.close()

                    except Exception:
                        pass

            except Exception:
                pass

    def get_all_timestamps(self) -> list:
        return [wt.to_dict() for wt in self._all_timestamps]
