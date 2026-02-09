from PySide6.QtWidgets import QStatusBar
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def setup_statusbar(self):
    try:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(QCoreApplication.translate("App", "Pronto"))
        self.tabs.currentChanged.connect(self.on_tab_changed)

    except Exception as e:
        logger.critical(f"Erro crítico ao configurar barra de status: {str(e)}", exc_info=True)
        raise
