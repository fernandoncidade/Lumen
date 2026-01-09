from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def closeEvent(self, event):
    try:
        if hasattr(self, 'leitor') and self.leitor:
            try:
                self.leitor.cleanup()

            except Exception:
                pass

        if hasattr(self, 'leitor') and self.leitor and hasattr(self.leitor, 'regua') and self.leitor.regua:
            try:
                self.leitor.regua.close()

            except Exception:
                pass

        if hasattr(self, 'gerenciador') and self.gerenciador:
            try:
                if hasattr(self.gerenciador, 'cleanup'):
                    self.gerenciador.cleanup()

            except Exception:
                pass

        try:
            if hasattr(self, 'mapa') and getattr(self, 'mapa'):
                if hasattr(self.mapa, 'cleanup'):
                    try:
                        self.mapa.cleanup()

                    except Exception:
                        pass

        except Exception:
            pass

        event.accept()

    except Exception as e:
        logger.error(f"Erro ao fechar aplicação: {str(e)}", exc_info=True)
        event.accept()
