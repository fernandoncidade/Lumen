from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def atualizar_interface(self, codigo_idioma):
    try:
        self.setWindowTitle(QCoreApplication.translate("App", "Lúmen"))
        if not hasattr(self, 'tabs'):
            return

        self.tabs.setTabText(0, QCoreApplication.translate("App", "📖 Leitor Acessível"))
        self.tabs.setTabText(1, QCoreApplication.translate("App", "⏱️ Gestão de Tempo"))
        self.tabs.setTabText(2, QCoreApplication.translate("App", "🧠 Mapas Mentais"))
        self.tabs.setTabText(3, QCoreApplication.translate("App", "🎓 Método Feynman"))
        self.tabs.setTabText(4, QCoreApplication.translate("App", "🗂️ Matriz Eisenhower"))

        self.atualizar_menu()

        if hasattr(self, 'status_bar'):
            tab_name = self.tabs.tabText(self.tabs.currentIndex())
            self.status_bar.showMessage(QCoreApplication.translate("App", "Módulo ativo: {tab_name}").format(tab_name=tab_name))

        if hasattr(self, 'menu_sobre'):
            self.menu_sobre.setTitle(QCoreApplication.translate("App", "ℹ️ Sobre"))

        if hasattr(self, 'action_sobre_app'):
            self.action_sobre_app.setText(QCoreApplication.translate("App", "ℹ️ Sobre o Aplicativo"))

    except Exception as e:
        logger.error(f"Erro ao atualizar interface: {str(e)}", exc_info=True)
