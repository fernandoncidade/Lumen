from source.utils.LogManager import LogManager
import os
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer
import time

logger = LogManager.get_logger()

def definir_voz(self, voz_id):
    try:
        try:
            self._changing_voice = True

        except Exception:
            pass

        try:
            t = getattr(self, "tts_thread", None)
            if t is not None:
                try:
                    t.chunk_ready.disconnect(self._play_generated_audio)

                except Exception:
                    pass

                try:
                    t.error.disconnect()

                except Exception:
                    pass

                try:
                    if hasattr(t, "stop"):
                        t.stop()

                except Exception:
                    pass

                try:
                    if getattr(t, "isRunning", None) and t.isRunning():
                        t.wait(3000)

                except Exception:
                    pass

                try:
                    if getattr(t, "isRunning", None) and t.isRunning():
                        logger.warning("Thread TTS ainda em execução após stop/wait; não terminarei a thread bruscamente para evitar corrotinas pendentes.")
                        try:
                            t.wait(2000)

                        except Exception:
                            pass

                except Exception:
                    pass

                try:
                    self.tts_thread = None

                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"Erro ao parar thread TTS antes de mudar voz: {e}", exc_info=True)

        try:
            if hasattr(self, "player") and self.player is not None:
                try:
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

        except Exception:
            pass

        try:
            files = getattr(self, "_generated_files", None) or []
            current = getattr(self, "_current_generated", None)

            playing_current = False
            try:
                if current and hasattr(self, "player") and self.player is not None:
                    if self.player.playbackState() == QMediaPlayer.PlayingState:
                        playing_current = True

            except Exception:
                playing_current = False

            for f in list(files):
                try:
                    if not f:
                        continue

                    if f == current and playing_current:
                        continue

                    if os.path.exists(f):
                        try:
                            os.remove(f)

                        except Exception:
                            logger.debug(f"Falha ao remover arquivo temporário durante mudança de voz (ignorando): {f}", exc_info=True)

                except Exception:
                    pass

            if current and playing_current and os.path.exists(current):
                self._generated_files = [current]
                self._generated_queue = []

            else:
                self._generated_files = []
                self._generated_queue = []
                self._current_generated = None

        except Exception as e:
            logger.debug(f"Erro ao limpar arquivos gerados durante mudança de voz: {e}", exc_info=True)

        self.voz_id_atual = voz_id

    except Exception as e:
        logger.error(f"Erro ao definir voz '{voz_id}': {str(e)}", exc_info=True)

    finally:
        try:
            time.sleep(0.05)

        except Exception:
            pass

        try:
            self._changing_voice = False

        except Exception:
            pass
