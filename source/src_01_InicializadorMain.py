import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from source.utils.LogManager import LogManager
from source.utils.IconUtils import get_icon_path
logger = LogManager.get_logger()

def configurar_windows_app_id():
    try:
        import ctypes
        myappid = 'fernandoncidade.lumen.estudoacessivel.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        logger.debug("AppUserModelID configurado para Windows")

    except Exception as e:
        logger.warning(f"Não foi possível configurar AppUserModelID: {e}")

def configurar_aplicacao():
    app = QApplication(sys.argv)
    app.setApplicationName("Lúmen")
    app.setOrganizationName("fernandoncidade")
    app.setOrganizationDomain("fernandoncidade.github.io")
    return app

def configurar_icone_aplicacao(app):
    icon_path = get_icon_path("autismo.ico")
    logger.debug(f"Tentando carregar ícone de: {icon_path}")

    if icon_path and os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        available_sizes = app_icon.availableSizes()
        logger.debug(f"Tamanhos disponíveis do ícone: {available_sizes}")

        if not app_icon.isNull() and available_sizes:
            app.setWindowIcon(app_icon)
            logger.info(f"✓ Ícone da aplicação configurado com sucesso: {icon_path}")
            return app_icon

        else:
            logger.error(f"✗ Ícone carregado está nulo ou sem tamanhos: {icon_path}")

    else:
        logger.error(f"✗ Caminho do ícone não encontrado ou não existe: {icon_path}")

    return None

def criar_janela_principal():
    from source import EstudoAcessivel
    return EstudoAcessivel()

def configurar_icone_janela(window, app_icon):
    if app_icon:
        window.setWindowIcon(app_icon)

def iniciar_aplicacao():
    try:
        configurar_windows_app_id()
        app = configurar_aplicacao()
        app_icon = configurar_icone_aplicacao(app)
        window = criar_janela_principal()
        # from source.utils.TrialManager import TrialManager
        # TrialManager.enforce_trial()
        # TrialManager.delete_first_run_timestamp()

        window.show()
        configurar_icone_janela(window, app_icon)

        exit_code = app.exec()
        logger.debug(f"Aplicação encerrada com código de saída: {exit_code}")

        return exit_code

    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar aplicação: {e}", exc_info=True)
        return 1
