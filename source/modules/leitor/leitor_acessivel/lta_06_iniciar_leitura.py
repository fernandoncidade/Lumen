from PySide6.QtMultimedia import QMediaPlayer
from source.modules.leitor.lt_01_TTSThread import TTSThread
from source.modules.leitor.lt_02_EdgeTTSThread import EdgeTTSThread
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

            return

        texto = ""
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
                # Aba PDF: decidir entre ler página atual ou todo o documento conforme modo de rolagem
                texto = ""
                arquivo = getattr(self, "_last_pdf_path", None)
                mode = getattr(self, "_pdf_scroll_mode", "continuous")
                if arquivo:
                    # Se modo continuous => ler todas as páginas sequencialmente
                    if mode == "continuous":
                        try:
                            import pdfplumber
                            parts = []
                            with pdfplumber.open(arquivo) as pdf:
                                for p in pdf.pages:
                                    try:
                                        parts.append(p.extract_text() or "")
                                    except Exception:
                                        parts.append(p.extract_text(x_tolerance=2, y_tolerance=3) or "")
                            texto = "\n\n".join(parts).strip()
                        except Exception:
                            try:
                                from PyPDF2 import PdfReader
                                reader = PdfReader(arquivo)
                                parts = []
                                for p in reader.pages:
                                    try:
                                        parts.append(p.extract_text() or "")
                                    except Exception:
                                        parts.append("")
                                texto = "\n\n".join(parts).strip()
                            except Exception:
                                texto = ""
                    else:
                        # modo page => comportamento anterior: ler página atual (spin_page) ou todo doc caso inválido
                        page_num = 0
                        try:
                            page_num = int(self.spin_page.value()) - 1 if hasattr(self, "spin_page") else 0
                        except Exception:
                            page_num = 0

                        try:
                            import pdfplumber
                            with pdfplumber.open(arquivo) as pdf:
                                if 0 <= page_num < len(pdf.pages):
                                    texto = pdf.pages[page_num].extract_text() or ""
                                else:
                                    texto = "\n\n".join((p.extract_text() or "") for p in pdf.pages)
                        except Exception:
                            try:
                                from PyPDF2 import PdfReader
                                reader = PdfReader(arquivo)
                                if 0 <= page_num < len(reader.pages):
                                    texto = reader.pages[page_num].extract_text() or ""
                                else:
                                    parts = []
                                    for p in reader.pages:
                                        try:
                                            parts.append(p.extract_text() or "")
                                        except Exception:
                                            parts.append("")
                                    texto = "\n\n".join(parts)
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

            self.tts_thread = EdgeTTSThread(
                texto=texto,
                voz=voz_para_usar,
                rate_pct=rate_pct,
                volume_pct=0
            )
            self.tts_thread.chunk_ready.connect(self._play_generated_audio)
            self.tts_thread.error.connect(lambda err: self._on_tts_error(err))
            self.tts_thread.start()

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
