from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def regua_fechada(self):
    try:
        self.regua = None
        self.gerenciador_botoes.set_button_text(self.btn_regua, QCoreApplication.translate("App", "📏 Ativar Régua de Foco"))
        self.btn_regua.setStyleSheet("")
        self.btn_regua.setChecked(False)

        from PySide6.QtWidgets import QApplication
        main_window = QApplication.instance().activeWindow()
        if hasattr(main_window, 'action_regua_foco'):
            main_window.action_regua_foco.setChecked(False)

    except Exception as e:
        logger.error(f"Erro ao processar fechamento da régua: {str(e)}", exc_info=True)
