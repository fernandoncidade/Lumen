from PySide6.QtCore import QThread, Signal
import pyttsx3
from source.utils.LogManager import LogManager


class TTSThread(QThread):
    finished = Signal()

    def __init__(self, texto, velocidade=150, volume=1.0, voz_id=None):
        super().__init__()
        self.texto = texto
        self.velocidade = velocidade
        self.volume = volume
        self.voz_id = voz_id
        self.engine = None
        self.logger = LogManager.get_logger()
        self._is_running = False

    def run(self):
        try:
            self._is_running = True
            self.engine = pyttsx3.init()
            if self.voz_id:
                try:
                    self.engine.setProperty('voice', self.voz_id)

                except Exception as e:
                    self.logger.error(f"Falha ao aplicar voz '{self.voz_id}': {e}")

            self.engine.setProperty('rate', self.velocidade)
            self.engine.setProperty('volume', self.volume)
            self.engine.say(self.texto)
            self.engine.runAndWait()
            self._is_running = False
            self.finished.emit()

        except Exception as e:
            self.logger.error(f"Erro ao executar Text-to-Speech: {str(e)}", exc_info=True)
            self._is_running = False
            self.finished.emit()

    def stop(self):
        try:
            self._is_running = False
            if self.engine:
                self.engine.stop()

        except Exception as e:
            self.logger.error(f"Erro ao parar Text-to-Speech: {str(e)}", exc_info=True)
