from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
from .lta_32_speech_highlight import SpeechHighlightManager, HighlightMode, HighlightStyle, SpeechHighlightSettings
logger = LogManager.get_logger()

def _init_speech_highlight(self):
    try:
        if not hasattr(self, "texto_area") or self.texto_area is None:
            logger.debug("texto_area não disponível para inicializar speech highlight")
            return

        self._speech_highlight_manager = SpeechHighlightManager(self.texto_area, self)
        self._speech_highlight_manager.set_style(SpeechHighlightSettings.get_default_style())
        self._speech_highlight_manager.set_mode(SpeechHighlightSettings.get_default_mode())
        self._speech_highlight_manager.word_highlighted.connect(lambda s, e: logger.debug(f"Palavra destacada: pos {s}-{e}"))

        logger.debug("SpeechHighlightManager inicializado com sucesso")

    except Exception as e:
        logger.error(f"Erro ao inicializar speech highlight: {e}", exc_info=True)
        self._speech_highlight_manager = None

def _setup_speech_highlight_for_reading(self, text: str):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            _init_speech_highlight(self)
            manager = getattr(self, "_speech_highlight_manager", None)
            if manager is None:
                logger.debug("Não foi possível inicializar speech highlight manager")
                return

        manager.stop()
        manager.clear_timestamps()
        self._accumulated_timestamps = []
        self._chunk_base_offsets = [0]
        self._current_chunk_index = 0
        manager.set_original_text(text)

        if hasattr(self, "player") and self.player is not None:
            manager.set_media_player(self.player)

        logger.debug(f"Speech highlight configurado para nova leitura (texto com {len(text)} caracteres)")

    except Exception as e:
        logger.debug(f"Erro ao configurar speech highlight: {e}", exc_info=True)

def _on_timestamps_received(self, timestamps: list):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            _init_speech_highlight(self)
            manager = getattr(self, "_speech_highlight_manager", None)
            if manager is None:
                return

        if not timestamps:
            return

        if not hasattr(self, "_accumulated_timestamps") or self._accumulated_timestamps is None:
            self._accumulated_timestamps = []

        if not hasattr(self, "_chunk_base_offsets") or self._chunk_base_offsets is None:
            self._chunk_base_offsets = [0]

        current_timestamps = self._accumulated_timestamps
        if not current_timestamps:
            manager.set_timestamps(timestamps, append=False)
            self._accumulated_timestamps = list(timestamps)

        else:
            try:
                last = current_timestamps[-1]
                base_offset = int(last.get("offset_ms", 0)) + int(last.get("duration_ms", 0))
                self._chunk_base_offsets.append(base_offset)

            except Exception:
                pass

            manager.set_timestamps(timestamps, append=True)
            self._accumulated_timestamps.extend(timestamps)

        logger.debug(f"Timestamps recebidos: {len(timestamps)} palavras, total: {len(self._accumulated_timestamps)}")

        if not manager._is_active and manager.is_enabled():
            manager.start(0)

    except Exception as e:
        logger.debug(f"Erro ao processar timestamps recebidos: {e}", exc_info=True)

def _start_speech_highlight(self):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None or not manager.is_enabled():
            return

        if not hasattr(self, "_accumulated_timestamps"):
            self._accumulated_timestamps = []

        if self._accumulated_timestamps:
            manager.start(0)
            logger.debug("Speech highlight iniciado com timestamps existentes")

        else:
            logger.debug("Speech highlight aguardando timestamps...")

    except Exception as e:
        logger.debug(f"Erro ao iniciar speech highlight: {e}", exc_info=True)

def _pause_speech_highlight(self):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            return

        manager.pause()
        logger.debug("Speech highlight pausado")

    except Exception as e:
        logger.debug(f"Erro ao pausar speech highlight: {e}", exc_info=True)

def _resume_speech_highlight(self):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            return

        manager.resume()
        logger.debug("Speech highlight retomado")

    except Exception as e:
        logger.debug(f"Erro ao retomar speech highlight: {e}", exc_info=True)

def _stop_speech_highlight(self):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            return

        manager.stop()
        self._accumulated_timestamps = []
        self._chunk_base_offsets = [0]
        self._current_chunk_index = 0
        logger.debug("Speech highlight parado")

    except Exception as e:
        logger.debug(f"Erro ao parar speech highlight: {e}", exc_info=True)

def toggle_speech_highlight(self):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            _init_speech_highlight(self)
            manager = getattr(self, "_speech_highlight_manager", None)
            if manager is None:
                return

        new_state = not manager.is_enabled()
        manager.set_enabled(new_state)

        btn = getattr(self, "btn_highlight", None)
        if btn is not None:
            if new_state:
                btn.setText(QCoreApplication.translate("App", "🔦 Desativar Realce"))
                btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")

            else:
                btn.setText(QCoreApplication.translate("App", "🔦 Ativar Realce"))
                btn.setStyleSheet("")

        logger.debug(f"Speech highlight {'ativado' if new_state else 'desativado'}")

    except Exception as e:
        logger.error(f"Erro ao alternar speech highlight: {e}", exc_info=True)

def set_speech_highlight_mode(self, mode: str):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            return

        mode_map = {
            "word": HighlightMode.WORD,
            "sentence": HighlightMode.SENTENCE,
            "paragraph": HighlightMode.PARAGRAPH,
        }

        if mode.lower() in mode_map:
            manager.set_mode(mode_map[mode.lower()])
            logger.debug(f"Modo de highlight alterado para: {mode}")

    except Exception as e:
        logger.debug(f"Erro ao definir modo de highlight: {e}", exc_info=True)

def set_speech_highlight_style(self, background: str = None, foreground: str = None, bold: bool = None, underline: bool = None):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            return

        style = HighlightStyle()

        if background is not None:
            style.current_word_bg = background

        if foreground is not None:
            style.current_word_fg = foreground

        if bold is not None:
            style.bold = bold

        if underline is not None:
            style.underline = underline

        manager.set_style(style)
        logger.debug(f"Estilo de highlight atualizado")

    except Exception as e:
        logger.debug(f"Erro ao definir estilo de highlight: {e}", exc_info=True)

def set_speech_highlight_auto_scroll(self, enabled: bool):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            return

        manager.set_auto_scroll(enabled)
        logger.debug(f"Auto-scroll {'ativado' if enabled else 'desativado'}")

    except Exception as e:
        logger.debug(f"Erro ao configurar auto-scroll: {e}", exc_info=True)

def is_speech_highlight_enabled(self) -> bool:
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            return False

        return manager.is_enabled()

    except Exception:
        return False

def _on_toggle_leitura_assistida(self):
    try:
        btn = getattr(self, "btn_leitura_assistida", None)
        if btn is None:
            return

        is_checked = btn.isChecked()

        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            _init_speech_highlight(self)
            manager = getattr(self, "_speech_highlight_manager", None)

        if manager is not None:
            manager.set_enabled(is_checked)

            if is_checked:
                accumulated = getattr(self, "_accumulated_timestamps", None)
                if accumulated and len(accumulated) > 0:
                    if hasattr(self, "player") and self.player is not None:
                        manager.set_media_player(self.player)

                    if not manager._is_active:
                        manager.start(0)
                        logger.debug("Speech highlight reiniciado após reativação")

        pdf_manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if pdf_manager is not None:
            pdf_manager.set_enabled(is_checked)

            if is_checked:
                pdf_accumulated = getattr(self, "_pdf_accumulated_timestamps", None)
                if pdf_accumulated and len(pdf_accumulated) > 0:
                    if hasattr(self, "player") and self.player is not None:
                        pdf_manager.set_media_player(self.player)

                    if not pdf_manager._is_active:
                        pdf_manager.start(0)
                        logger.debug("PDF Speech highlight reiniciado após reativação")

        _update_leitura_assistida_button(self)

        combo = getattr(self, "combo_modo_leitura", None)
        if combo is not None:
            combo.setEnabled(is_checked)

        logger.debug(f"Leitura Assistida {'ativada' if is_checked else 'desativada'}")

    except Exception as e:
        logger.error(f"Erro ao alternar Leitura Assistida: {e}", exc_info=True)

def _on_modo_leitura_changed(self, index: int):
    try:
        mode_map = {
            0: "word",
            1: "sentence",
            2: "paragraph",
        }

        mode = mode_map.get(index, "word")

        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is not None:
            manager.set_mode(HighlightMode(mode))

        from .lta_34_pdf_speech_highlight import PDFHighlightMode
        pdf_manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if pdf_manager is not None:
            pdf_manager.set_mode(PDFHighlightMode(mode))

        logger.debug(f"Modo de Leitura Assistida alterado para: {mode}")

    except Exception as e:
        logger.error(f"Erro ao alterar modo de leitura: {e}", exc_info=True)

def _update_leitura_assistida_button(self):
    try:
        btn = getattr(self, "btn_leitura_assistida", None)
        if btn is None:
            return

        is_checked = btn.isChecked()

        if is_checked:
            texto = QCoreApplication.translate("App", "🔦 Desativar Leitura Assistida")
            btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")

        else:
            texto = QCoreApplication.translate("App", "🔦 Ativar Leitura Assistida")
            btn.setStyleSheet("")

        gerenciador = getattr(self, "gerenciador_botoes", None)
        if gerenciador is not None:
            gerenciador.set_button_text(btn, texto)

        else:
            btn.setText(texto)

    except Exception as e:
        logger.debug(f"Erro ao atualizar botão de Leitura Assistida: {e}", exc_info=True)

def _init_leitura_assistida_state(self):
    try:
        if not hasattr(self, "_speech_highlight_manager") or self._speech_highlight_manager is None:
            _init_speech_highlight(self)

        manager = getattr(self, "_speech_highlight_manager", None)
        btn = getattr(self, "btn_leitura_assistida", None)

        if manager is not None and btn is not None:
            is_enabled = manager.is_enabled()
            btn.setChecked(is_enabled)
            _update_leitura_assistida_button(self)

            combo = getattr(self, "combo_modo_leitura", None)
            if combo is not None:
                combo.setEnabled(is_enabled)

        logger.debug("Estado de Leitura Assistida inicializado")

    except Exception as e:
        logger.debug(f"Erro ao inicializar estado de Leitura Assistida: {e}", exc_info=True)

def _notify_chunk_changed(self, chunk_index: int, base_offset_ms: int | None = None):
    try:
        manager = getattr(self, "_speech_highlight_manager", None)
        if manager is None:
            return

        manager.notify_new_chunk_started(chunk_index, base_offset_ms=base_offset_ms)
        logger.debug(f"SpeechHighlightManager notificado: chunk {chunk_index}")

    except Exception as e:
        logger.debug(f"Erro ao notificar mudança de chunk: {e}", exc_info=True)

def _notify_pdf_chunk_changed(self, chunk_index: int, base_offset_ms: int | None = None):
    try:
        pdf_manager = getattr(self, "_pdf_speech_highlight_manager", None)
        if pdf_manager is None:
            return

        pdf_manager.notify_new_chunk_started(chunk_index, base_offset_ms=base_offset_ms)
        logger.debug(f"PDFSpeechHighlightManager notificado: chunk {chunk_index}")

    except Exception as e:
        logger.debug(f"Erro ao notificar mudança de chunk (PDF): {e}", exc_info=True)
