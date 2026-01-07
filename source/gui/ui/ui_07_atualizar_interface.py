from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def atualizar_interface(self, codigo_idioma):
    try:
        self.setWindowTitle(QCoreApplication.translate("App", "Lúmen"))
        if not hasattr(self, 'tabs'):
            return

        titles = {
            "leitor_acessivel": QCoreApplication.translate("App", "📖 Leitor Acessível"),
            "gestao_tempo": QCoreApplication.translate("App", "⏱️ Gestão de Tempo"),
            "mapas_mentais": QCoreApplication.translate("App", "🧠 Mapas Mentais"),
            "metodo_feynman": QCoreApplication.translate("App", "🎓 Método Feynman"),
            "matriz_eisenhower": QCoreApplication.translate("App", "🗂️ Matriz Eisenhower"),
        }
        
        tab_module_ids = getattr(self, "_tab_module_ids", None) or []
        for i in range(self.tabs.count()):
            if i < len(tab_module_ids):
                mid = tab_module_ids[i]
                if mid in titles:
                    self.tabs.setTabText(i, titles[mid])

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
