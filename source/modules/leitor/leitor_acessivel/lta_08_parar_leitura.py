from PySide6.QtCore import QThread, QUrl
from source.utils.LogManager import LogManager
import os

logger = LogManager.get_logger()

def parar_leitura(self):
    try:
        if self.usar_edge_tts:
            try:
                if hasattr(self, "player") and self.player is not None:
                    try:
                        self.player.stop()
                        try:
                            self.player.setSource(QUrl())

                        except Exception as e:
                            logger.debug(f"Erro ao ajustar source do player Edge TTS: {e}", exc_info=True)

                    except Exception as e:
                        logger.error(f"Erro ao parar player Edge TTS: {str(e)}", exc_info=True)

            except Exception as e:
                logger.error(f"Erro ao parar player Edge TTS: {str(e)}", exc_info=True)

            if self.tts_thread and isinstance(self.tts_thread, QThread) and self.tts_thread.isRunning():
                try:
                    if hasattr(self.tts_thread, "stop"):
                        try:
                            self.tts_thread.stop()
                            self.tts_thread.wait(3000)

                        except Exception as e:
                            logger.debug(f"Erro ao solicitar parada do EdgeTTSThread: {e}", exc_info=True)

                    if getattr(self.tts_thread, "isRunning", None) and self.tts_thread.isRunning():
                        logger.warning("EdgeTTSThread ainda em execução após stop/wait; aguardando mais tempo (evitando terminate).")
                        try:
                            self.tts_thread.wait(3000)

                        except Exception:
                            pass

                        if getattr(self.tts_thread, "isRunning", None) and self.tts_thread.isRunning():
                            logger.error("EdgeTTSThread não encerrou após tentativas de parada. Não foi utilizado terminate para evitar vazamento de recursos assíncronos.")

                except Exception as e:
                    logger.error(f"Erro ao finalizar EdgeTTSThread: {e}", exc_info=True)

            try:
                files = getattr(self, "_generated_files", []) or []
                for f in list(files):
                    try:
                        if f and os.path.exists(f):
                            os.remove(f)

                    except Exception:
                        logger.debug(f"Falha ao remover arquivo temporário TTS: {f}", exc_info=True)

                self._generated_files = []
                self._generated_queue = []
                self._current_generated = None

            except Exception as e:
                logger.error(f"Erro ao limpar arquivos gerados: {e}", exc_info=True)

        else:
            try:
                if self.tts_thread:
                    try:
                        if hasattr(self.tts_thread, "stop"):
                            self.tts_thread.stop()
                            try:
                                self.tts_thread.wait(500)

                            except Exception:
                                pass

                        if getattr(self.tts_thread, "isRunning", None) and self.tts_thread.isRunning():
                            try:
                                self.tts_thread.terminate()
                                self.tts_thread.wait(500)

                            except Exception as e:
                                logger.debug(f"Erro ao terminar TTSThread: {e}", exc_info=True)

                    except Exception as e:
                        logger.debug(f"Erro ao parar TTSThread: {e}", exc_info=True)

            except Exception as e:
                logger.error(f"Erro ao parar TTSThread: {str(e)}", exc_info=True)

        self._is_paused = False
        self._update_pause_button()
        try:
            cursor = self.texto_area.textCursor()
            cursor.clearSelection()
            cursor.setPosition(0)
            self.texto_area.setTextCursor(cursor)

        except Exception as e:
            logger.debug(f"Erro ao ajustar cursor do texto_area: {e}", exc_info=True)

        try:
            if getattr(self, "_pdf_mouse_handler", None):
                self._pdf_mouse_handler.set_mode("default")

        except Exception as e:
            logger.debug(f"Erro ao ajustar modo do _pdf_mouse_handler: {e}", exc_info=True)

        self.leitura_finalizada()

    except Exception as e:
        logger.error(f"Erro ao executar parar_leitura: {str(e)}", exc_info=True)
