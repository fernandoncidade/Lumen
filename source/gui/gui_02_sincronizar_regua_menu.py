from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def sincronizar_regua_menu(self, estado):
    try:
        if hasattr(self, 'action_regua_foco'):
            self.action_regua_foco.setChecked(estado)

    except Exception as e:
        logger.error(f"Erro ao sincronizar menu da régua: {str(e)}", exc_info=True)
