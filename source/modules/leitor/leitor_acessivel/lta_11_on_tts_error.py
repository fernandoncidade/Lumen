from PySide6.QtWidgets import QMessageBox
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _on_tts_error(self, err):
    logger.error(f"Erro no Edge TTS: {err}", exc_info=True)
    QMessageBox.warning(self, "TTS", f"Erro no TTS: {err}")
    self.leitura_finalizada()
