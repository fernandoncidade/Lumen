from PySide6.QtMultimedia import QMediaPlayer
from source.modules.leitor.lt_01_TTSThread import TTSThread
from source.modules.leitor.lt_04_EdgeTTSWithTimestamps import EdgeTTSWithTimestamps
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def iniciar_leitura(self):
    try:
        if self.usar_edge_tts and getattr(self, "player", None) is not None and self.player.playbackState() == QMediaPlayer.PausedState:
            self.player.play()
            self._is_paused = False
            self._update_pause_button()
            self.btn_play.setEnabled(False)
            self.btn_pause.setEnabled(True)
            if self.btn_stop is not None:
                self.btn_stop.setEnabled(True)

            self._resume_speech_highlight()
            self._resume_pdf_speech_highlight()

            return

        texto = ""
        pdf_path = None
        try:
            active_idx = 0
            if hasattr(self, "_content_stack") and self._content_stack is not None:
                try:
                    active_idx = self._content_stack.currentIndex()

                except Exception as e:
                    logger.debug(f"Erro ao obter índice da aba ativa: {e}", exc_info=True)
                    active_idx = 0

            if active_idx == 0:
                cursor = self.texto_area.textCursor()
                texto = cursor.selectedText() if cursor.hasSelection() else self.texto_area.toPlainText()

            else:
                texto = ""
                arquivo = getattr(self, "_last_pdf_path", None)
                pdf_path = arquivo
                mode = getattr(self, "_pdf_scroll_mode", "continuous")
                page_num = None
                if mode != "continuous":
                    try:
                        page_num = int(self.spin_page.value()) - 1 if hasattr(self, "spin_page") else 0

                    except Exception:
                        page_num = 0

                if arquivo:
                    try:
                        if hasattr(self, "_setup_pdf_speech_highlight_for_reading"):
                            texto = self._setup_pdf_speech_highlight_for_reading(arquivo, texto, page_index=page_num)

                        else:
                            texto = ""

                    except Exception:
                        texto = ""

                else:
                    texto = ""

        except Exception as e:
            logger.error(f"Erro ao obter texto para leitura a partir da aba ativa: {e}", exc_info=True)
            texto = ""

        if not texto:
            return

        velocidade = self.slider_velocidade.value()
        volume = self.slider_volume.value() / 100.0

        if self.usar_edge_tts:
            rate_pct = int(max(-50, min(50, round((velocidade - 150) / 2))))
            try:
                if getattr(self, "audio_output", None):
                    self.audio_output.setVolume(volume)

            except Exception as e:
                logger.debug(f"Erro ao ajustar volume do audio_output: {e}", exc_info=True)

            voz_para_usar = self.voz_id_atual or "pt-BR-AntonioNeural"

            try:
                active_idx = 0
                if hasattr(self, "_content_stack") and self._content_stack is not None:
                    try:
                        active_idx = self._content_stack.currentIndex()

                    except Exception:
                        active_idx = 0

                if active_idx == 0:
                    self._setup_speech_highlight_for_reading(texto)

                else:
                    pass

            except Exception as e:
                logger.debug(f"Erro ao configurar speech highlight: {e}", exc_info=True)

            self.tts_thread = EdgeTTSWithTimestamps(texto=texto, voz=voz_para_usar, rate_pct=rate_pct, volume_pct=0)
            self._current_reading_pdf_path = pdf_path
            self._current_chunk_index = 0

            def _on_chunk_ready_handler(audio_path, timestamps):
                self._play_generated_audio(audio_path)
                if timestamps:
                    try:
                        active_idx = 0
                        if hasattr(self, "_content_stack") and self._content_stack is not None:
                            try:
                                active_idx = self._content_stack.currentIndex()

                            except Exception:
                                active_idx = 0

                        if active_idx == 0:
                            self._on_timestamps_received(timestamps)

                        else:
                            self._on_pdf_timestamps_received(timestamps)

                    except Exception as e:
                        logger.debug(f"Erro ao processar timestamps: {e}", exc_info=True)

            self._chunk_ready_handler = _on_chunk_ready_handler
            self.tts_thread.chunk_ready.connect(self._chunk_ready_handler)
            self.tts_thread.error.connect(lambda err: self._on_tts_error(err))
            self.tts_thread.start()

            try:
                active_idx = 0
                if hasattr(self, "_content_stack") and self._content_stack is not None:
                    try:
                        active_idx = self._content_stack.currentIndex()

                    except Exception:
                        active_idx = 0

                if active_idx == 0:
                    self._start_speech_highlight()

                else:
                    self._start_pdf_speech_highlight()

            except Exception as e:
                logger.debug(f"Erro ao iniciar speech highlight: {e}", exc_info=True)

        else:
            self.tts_thread = TTSThread(texto, velocidade, volume, self.voz_id_atual)
            self.tts_thread.finished.connect(self.leitura_finalizada)
            self.tts_thread.start()

        self._is_paused = False
        self._update_pause_button()
        self.btn_pause.setEnabled(True)
        self.btn_play.setEnabled(False)
        if self.btn_stop is not None:
            self.btn_stop.setEnabled(True)

    except Exception as e:
        logger.error(f"Erro ao iniciar leitura: {str(e)}", exc_info=True)
