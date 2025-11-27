from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _update_pause_button(self):
    try:
        paused = getattr(self, "_is_paused", False)
        if paused:
            self.btn_pause.setText(QCoreApplication.translate("App", "▶️ Continuar"))
            if not self.btn_pause.isChecked():
                self.btn_pause.setChecked(True)

        else:
            self.btn_pause.setText(QCoreApplication.translate("App", "⏸️ Pausar"))
            if self.btn_pause.isChecked():
                self.btn_pause.setChecked(False)

    except Exception as e:
        logger.error(f"Erro ao atualizar botão de pausa: {str(e)}", exc_info=True)
