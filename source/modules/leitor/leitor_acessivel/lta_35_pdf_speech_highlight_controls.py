from source.utils.LogManager import LogManager
from .lta_34_pdf_speech_highlight import PDFSpeechHighlightManager, PDFHighlightMode, PDFHighlightStyle, extract_word_positions_from_pdf
logger = LogManager.get_logger()

def _init_pdf_speech_highlight(self):
    try:
        if not hasattr(self, "pdf_view") or self.pdf_view is None:
            logger.debug("[PDF] pdf_view não disponível para inicializar speech highlight")
            return

        self._pdf_speech_highlight_manager = PDFSpeechHighlightManager(self.pdf_view, self)
        self._pdf_speech_highlight_manager.set_style(PDFHighlightStyle())

        btn = getattr(self, "btn_leitura_assistida", None)
        if btn is not None:
            is_enabled = btn.isChecked()
            self._pdf_speech_highlight_manager.set_enabled(is_enabled)
            logger.debug(f"[PDF] Estado enabled sincronizado com botão: {is_enabled}")

        current_mode = PDFHighlightMode.WORD
        if hasattr(self, "_speech_highlight_manager") and self._speech_highlight_manager is not None:
            text_mode = getattr(self._speech_highlight_manager, "_mode", None)
            if text_mode is not None:
                mode_name = text_mode.value.lower() if hasattr(text_mode, 'value') else str(text_mode).lower()
                mode_map = {
                    "word": PDFHighlightMode.WORD,
                    "sentence": PDFHighlightMode.SENTENCE,
                    "paragraph": PDFHighlightMode.PARAGRAPH,
                }
                current_mode = mode_map.get(mode_name, PDFHighlightMode.WORD)
                logger.debug(f"[PDF] Modo herdado do texto: {current_mode.value}")

        self._pdf_speech_highlight_manager.set_mode(current_mode)
        self._pdf_speech_highlight_manager.word_highlighted.connect(lambda idx, rect: logger.debug(f"[PDF] Palavra destacada: idx {idx}, página {rect.page_index}"))

        logger.debug("[PDF] PDFSpeechHighlightManager inicializado com sucesso")

    except Exception as e:
        logger.error(f"[PDF] Erro ao inicializar pdf speech highlight: {e}", exc_info=True)
        self._pdf_speech_highlight_manager = None


def _setup_pdf_speech_highlight_for_reading(self, pdf_path: str, text: str, page_index: int | None = None) -> str:
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None:
            _init_pdf_speech_highlight(self)
            manager = getattr(self, "_pdf_speech_highlight_manager", None)
            if manager is None:
                logger.debug("[PDF] Não foi possível inicializar pdf speech highlight manager")
                return text or ""

        manager.stop()
        manager.clear_timestamps()
        self._pdf_accumulated_timestamps = []
        self._pdf_chunk_base_offsets = [0]

        try:
            extracted_text, word_rects, mapping = extract_word_positions_from_pdf(pdf_path, page_index=page_index)
            manager.set_word_positions(word_rects)
            manager.set_text_to_pdf_mapping(mapping)
            manager.set_extracted_text(extracted_text)
            setattr(self, "_pdf_speech_extracted_text", extracted_text)
            logger.debug(f"[PDF] Posições de palavras extraídas: {len(word_rects)} palavras, texto com {len(extracted_text)} caracteres")

        except Exception as e:
            logger.debug(f"[PDF] Erro ao extrair posições de palavras: {e}", exc_info=True)
            manager.set_extracted_text(text)
            setattr(self, "_pdf_speech_extracted_text", text or "")

        if hasattr(self, "player") and self.player is not None:
            manager.set_media_player(self.player)

        logger.debug(f"[PDF] Speech highlight configurado para nova leitura")
        return getattr(self, "_pdf_speech_extracted_text", text or "")

    except Exception as e:
        logger.debug(f"[PDF] Erro ao configurar pdf speech highlight: {e}", exc_info=True)
        return text or ""

def _on_pdf_timestamps_received(self, timestamps: list):
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None:
            _init_pdf_speech_highlight(self)
            manager = getattr(self, "_pdf_speech_highlight_manager", None)
            if manager is None:
                return

        if not timestamps:
            return

        if not hasattr(self, "_pdf_accumulated_timestamps") or self._pdf_accumulated_timestamps is None:
            self._pdf_accumulated_timestamps = []

        if not hasattr(self, "_pdf_chunk_base_offsets") or self._pdf_chunk_base_offsets is None:
            self._pdf_chunk_base_offsets = [0]

        current_timestamps = self._pdf_accumulated_timestamps
        if not current_timestamps:
            manager.set_timestamps(timestamps, append=False)
            self._pdf_accumulated_timestamps = list(timestamps)

        else:
            try:
                last = current_timestamps[-1]
                base_offset = int(last.get("offset_ms", 0)) + int(last.get("duration_ms", 0))
                self._pdf_chunk_base_offsets.append(base_offset)

            except Exception:
                pass

            manager.set_timestamps(timestamps, append=True)
            self._pdf_accumulated_timestamps.extend(timestamps)

        logger.debug(f"[PDF] Timestamps recebidos: {len(timestamps)} palavras, total: {len(self._pdf_accumulated_timestamps)}")

        if not manager._is_active and manager.is_enabled():
            manager.start(0)

    except Exception as e:
        logger.debug(f"[PDF] Erro ao processar timestamps recebidos: {e}", exc_info=True)

def _start_pdf_speech_highlight(self):
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None or not manager.is_enabled():
            return

        if not hasattr(self, "_pdf_accumulated_timestamps"):
            self._pdf_accumulated_timestamps = []

        if self._pdf_accumulated_timestamps:
            manager.start(0)
            logger.debug("[PDF] Speech highlight iniciado com timestamps existentes")

        else:
            logger.debug("[PDF] Speech highlight aguardando timestamps...")

    except Exception as e:
        logger.debug(f"[PDF] Erro ao iniciar pdf speech highlight: {e}", exc_info=True)

def _pause_pdf_speech_highlight(self):
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None:
            return

        manager.pause()
        logger.debug("[PDF] Speech highlight pausado")

    except Exception as e:
        logger.debug(f"[PDF] Erro ao pausar pdf speech highlight: {e}", exc_info=True)

def _resume_pdf_speech_highlight(self):
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None:
            return

        manager.resume()
        logger.debug("[PDF] Speech highlight retomado")

    except Exception as e:
        logger.debug(f"[PDF] Erro ao retomar pdf speech highlight: {e}", exc_info=True)

def _stop_pdf_speech_highlight(self):
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None:
            return

        manager.stop()
        self._pdf_accumulated_timestamps = []
        self._pdf_chunk_base_offsets = [0]
        logger.debug("[PDF] Speech highlight parado")

    except Exception as e:
        logger.debug(f"[PDF] Erro ao parar pdf speech highlight: {e}", exc_info=True)

def toggle_pdf_speech_highlight(self):
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None:
            _init_pdf_speech_highlight(self)
            manager = getattr(self, "_pdf_speech_highlight_manager", None)
            if manager is None:
                return

        new_state = not manager.is_enabled()
        manager.set_enabled(new_state)

        logger.debug(f"[PDF] Speech highlight {'ativado' if new_state else 'desativado'}")

    except Exception as e:
        logger.error(f"[PDF] Erro ao alternar pdf speech highlight: {e}", exc_info=True)

def set_pdf_speech_highlight_mode(self, mode: str):
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None:
            return

        mode_map = {
            "word": PDFHighlightMode.WORD,
            "sentence": PDFHighlightMode.SENTENCE,
            "paragraph": PDFHighlightMode.PARAGRAPH,
        }

        if mode.lower() in mode_map:
            manager.set_mode(mode_map[mode.lower()])
            logger.debug(f"[PDF] Modo de highlight alterado para: {mode}")

    except Exception as e:
        logger.debug(f"[PDF] Erro ao definir modo de highlight: {e}", exc_info=True)

def is_pdf_speech_highlight_enabled(self) -> bool:
    try:
        manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if manager is None:
            return False

        return manager.is_enabled()

    except Exception:
        return False
