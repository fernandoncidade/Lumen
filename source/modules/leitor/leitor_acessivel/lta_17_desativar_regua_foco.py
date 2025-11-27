from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def desativar_regua_foco(self):
    try:
        if self.regua is not None:
            self.regua.close()
            self.regua = None

        self.gerenciador_botoes.set_button_text(self.btn_regua, QCoreApplication.translate("App", "📏 Ativar Régua de Foco"))
        self.btn_regua.setStyleSheet("")
        self.btn_regua.setChecked(False)

    except Exception as e:
        logger.error(f"Erro ao desativar régua de foco: {str(e)}", exc_info=True)
