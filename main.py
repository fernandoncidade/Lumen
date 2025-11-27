import sys
from PySide6.QtWidgets import QApplication
from source.utils.LogManager import LogManager
# from source.utils.TrialManager import TrialManager

logger = LogManager.get_logger()


def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Lúmen")

        from source import EstudoAcessivel
        window = EstudoAcessivel()

        # TrialManager.enforce_trial()  # Descomente esta linha para forçar o uso da versão de avaliação
        # TrialManager.delete_first_run_timestamp()  # Use esta linha para testes, removendo o timestamp de primeiro uso

        window.show()
        exit_code = app.exec()
        logger.debug(f"Aplicação encerrada com código de saída: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar aplicação: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
