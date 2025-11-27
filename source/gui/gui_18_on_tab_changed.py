from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def on_tab_changed(self, index):
    try:
        tab_name = self.tabs.tabText(index)
        self.status_bar.showMessage(QCoreApplication.translate("App", "Módulo ativo: {tab_name}").format(tab_name=tab_name))

    except Exception as e:
        logger.critical(f"Erro crítico ao processar mudança de aba: {str(e)}", exc_info=True)
