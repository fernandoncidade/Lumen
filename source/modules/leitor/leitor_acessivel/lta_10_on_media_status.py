from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import QUrl
from source.utils.LogManager import LogManager
import os
logger = LogManager.get_logger()

def _on_media_status(self, status):
    try:
        if status == QMediaPlayer.EndOfMedia:
            try:
                prev = getattr(self, "_current_generated", None)

                if getattr(self, "_generated_queue", None):
                    next_path = self._generated_queue.pop(0)
                    self._current_generated = next_path
                    self.player.setSource(QUrl.fromLocalFile(next_path))
                    self.player.play()

                    if not hasattr(self, "_current_chunk_index"):
                        self._current_chunk_index = 0

                    self._current_chunk_index += 1

                    try:
                        active_idx = 0
                        if hasattr(self, "_content_stack") and self._content_stack is not None:
                            try:
                                active_idx = self._content_stack.currentIndex()

                            except Exception:
                                active_idx = 0

                        if active_idx == 0:
                            base_offset = None
                            try:
                                offsets = getattr(self, "_chunk_base_offsets", None)
                                if isinstance(offsets, list) and 0 <= self._current_chunk_index < len(offsets):
                                    base_offset = offsets[self._current_chunk_index]

                            except Exception:
                                base_offset = None

                            if base_offset is None:
                                try:
                                    acc = getattr(self, "_accumulated_timestamps", None) or []
                                    if acc:
                                        last = acc[-1]
                                        base_offset = int(last.get("offset_ms", 0)) + int(last.get("duration_ms", 0))

                                except Exception:
                                    base_offset = None

                            self._notify_chunk_changed(self._current_chunk_index, base_offset)

                        else:
                            base_offset = None
                            try:
                                offsets = getattr(self, "_pdf_chunk_base_offsets", None)
                                if isinstance(offsets, list) and 0 <= self._current_chunk_index < len(offsets):
                                    base_offset = offsets[self._current_chunk_index]

                            except Exception:
                                base_offset = None

                            if base_offset is None:
                                try:
                                    acc = getattr(self, "_pdf_accumulated_timestamps", None) or []
                                    if acc:
                                        last = acc[-1]
                                        base_offset = int(last.get("offset_ms", 0)) + int(last.get("duration_ms", 0))

                                except Exception:
                                    base_offset = None

                            self._notify_pdf_chunk_changed(self._current_chunk_index, base_offset)

                    except Exception as e:
                        logger.debug(f"Erro ao notificar mudança de chunk: {e}", exc_info=True)

                    if prev and os.path.exists(prev):
                        try:
                            os.remove(prev)
                            if getattr(self, "_generated_files", None) and prev in self._generated_files:
                                try:
                                    self._generated_files.remove(prev)

                                except Exception as e:
                                    logger.debug(f"Falha ao remover chunk anterior da lista: {prev}", exc_info=True)

                        except Exception as e:
                            logger.debug(f"Não foi possível remover chunk anterior: {prev}", exc_info=True)

                    return

            except Exception as e:
                logger.error(f"Erro ao tocar próximo chunk: {e}", exc_info=True)

            try:
                if hasattr(self, "player") and self.player is not None:
                    try:
                        self.player.stop()

                    except Exception:
                        pass

                    try:
                        self.player.setSource(QUrl())

                    except Exception:
                        pass

            except Exception:
                pass

            try:
                from .lta_25_audio_temp_cleanup import cleanup_paths_with_retry, cleanup_edge_tts_temp_in_outdir

                files = list(getattr(self, "_generated_files", []) or [])
                queue = list(getattr(self, "_generated_queue", []) or [])
                current = getattr(self, "_current_generated", None)

                targets = []
                targets.extend(files)
                targets.extend(queue)
                if current:
                    targets.append(current)

                cleanup_paths_with_retry(self, targets)
                cleanup_edge_tts_temp_in_outdir(self, remove_mp3=True, remove_part=True)

            except Exception as e:
                logger.debug(f"Falha ao executar limpeza final com retry: {e}", exc_info=True)

            try:
                self._generated_queue = []
                self._generated_files = []
                self._current_generated = None

            except Exception as e:
                logger.debug(f"Erro ao limpar estado da fila: {e}", exc_info=True)

            self.leitura_finalizada()

        elif status == QMediaPlayer.InvalidMedia:
            cur = getattr(self, "_current_generated", None)
            if cur and os.path.exists(cur):
                try:
                    os.remove(cur)
                    if getattr(self, "_generated_files", None) and cur in self._generated_files:
                        try:
                            self._generated_files.remove(cur)

                        except Exception as e:
                            logger.debug(f"Falha ao remover mídia inválida da lista: {cur}", exc_info=True)

                except Exception as e:
                    logger.debug(f"Não foi possível remover mídia inválida: {cur}", exc_info=True)

            self._generated_queue = []
            self._current_generated = None
            self.leitura_finalizada()

    except Exception as e:
        logger.error(f"Erro no status do player: {str(e)}", exc_info=True)
