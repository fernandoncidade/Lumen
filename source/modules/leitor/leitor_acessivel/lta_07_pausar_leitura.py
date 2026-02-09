from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication
from PySide6.QtMultimedia import QMediaPlayer
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def pausar_leitura(self):
    try:
        if self.usar_edge_tts:
            estado = self.player.playbackState()
            if estado == QMediaPlayer.PlayingState:
                self.player.pause()
                self._is_paused = True
                self._update_pause_button()

            elif estado == QMediaPlayer.PausedState:
                self.player.play()
                self._is_paused = False
                self._update_pause_button()

            else:
                pass

        else:
            QMessageBox.information(
                self,
                QCoreApplication.translate("App", "Pausar"),
                QCoreApplication.translate("App", "Pausar/continuar está disponível apenas com as vozes neurais (Edge TTS).")
            )

    except Exception as e:
        logger.error(f"Erro ao alternar pausa/continuação: {str(e)}", exc_info=True)
