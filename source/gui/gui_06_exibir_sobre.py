from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def exibir_sobre(self):
    try:
        from source.modules.mod_07_exibir_public import exibir_sobre as _exibir_sobre
        parent = self
        _exibir_sobre(parent)

    except Exception as e:
        logger.error(f"Erro ao exibir diálogo Sobre (app): {e}", exc_info=True)
        QMessageBox.critical(self, QCoreApplication.translate("App", "Erro"), f"{QCoreApplication.translate('App','Erro')}: {e}")
