from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def toggle_regua_foco(self):
    try:
        if self.btn_regua.isChecked():
            self.ativar_regua_foco()

        else:
            self.desativar_regua_foco()

    except Exception as e:
        logger.error(f"Erro ao alternar régua de foco: {str(e)}", exc_info=True)
