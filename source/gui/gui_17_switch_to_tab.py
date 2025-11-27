from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def switch_to_tab(self, index):
    try:
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    except Exception as e:
        logger.critical(f"Erro crítico ao alternar para aba {index}: {str(e)}", exc_info=True)
