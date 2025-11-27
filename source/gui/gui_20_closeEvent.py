from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def closeEvent(self, event):
    try:
        if hasattr(self, 'leitor') and self.leitor:
            self.leitor.cleanup()

        if hasattr(self, 'leitor') and self.leitor and hasattr(self.leitor, 'regua') and self.leitor.regua:
            self.leitor.regua.close()

        event.accept()

    except Exception as e:
        logger.error(f"Erro ao fechar aplicação: {str(e)}", exc_info=True)
        event.accept()
