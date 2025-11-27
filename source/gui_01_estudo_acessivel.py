import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
from source.language.tr_01_gerenciadorTraducao import GerenciadorTraducao
from source.utils.IconUtils import get_icon_path
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente

logger = LogManager.get_logger()

try:
    base_persist = obter_caminho_persistente()
    if base_persist:
        try:
            QCoreApplication.setOrganizationName("Lumen")
            QCoreApplication.setApplicationName(os.path.basename(base_persist) or "Lúmen")

        except Exception as e:
            logger.error(f"Erro ao configurar nome da aplicação: {e}", exc_info=True)

except Exception as e:
    logger.error(f"Erro ao obter caminho persistente: {e}", exc_info=True)

class EstudoAcessivel(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.tradutor = GerenciadorTraducao()
            self.tradutor.idioma_alterado.connect(self.atualizar_interface)
            self.tradutor.aplicar_traducao()
            self.gerenciador_traducao = self.tradutor

            self.setup_ui()
            self.setup_menubar()
            self.setup_shortcuts()
            self.setup_statusbar()
            self.atualizar_interface(self.tradutor.obter_idioma_atual())
            self.setWindowTitle(QCoreApplication.translate("App", "Lúmen"))
            self.setMinimumSize(1200, 800)

            try:
                icon_path = get_icon_path("autismo.ico")
                if icon_path:
                    self.setWindowIcon(QIcon(icon_path))

            except Exception as e:
                logger.error(f"Erro ao carregar ícone da aplicação: {e}", exc_info=True)

        except Exception as e:
            logger.critical(f"Erro crítico ao inicializar EstudoAcessivelApp: {str(e)}", exc_info=True)
            raise

from source.gui import (
    setup_ui,
    sincronizar_regua_menu,
    setup_menubar,
    executar_acao_modulo,
    mudar_idioma,
    exibir_sobre,
    atualizar_interface,
    atualizar_menu,
    _get_persist_file,
    _salvar_voz_persistente,
    _carregar_voz_persistente,
    carregar_vozes,
    definir_voz,
    atualizar_modulos,
    setup_shortcuts,
    setup_statusbar,
    switch_to_tab,
    on_tab_changed,
    show_help,
    closeEvent,
    changeEvent
)

EstudoAcessivel.setup_ui = setup_ui
EstudoAcessivel.sincronizar_regua_menu = sincronizar_regua_menu
EstudoAcessivel.setup_menubar = setup_menubar
EstudoAcessivel.executar_acao_modulo = executar_acao_modulo
EstudoAcessivel.mudar_idioma = mudar_idioma
EstudoAcessivel.exibir_sobre = exibir_sobre
EstudoAcessivel.atualizar_interface = atualizar_interface
EstudoAcessivel.atualizar_menu = atualizar_menu
EstudoAcessivel._get_persist_file = _get_persist_file
EstudoAcessivel._salvar_voz_persistente = _salvar_voz_persistente
EstudoAcessivel._carregar_voz_persistente = _carregar_voz_persistente
EstudoAcessivel.carregar_vozes = carregar_vozes
EstudoAcessivel.definir_voz = definir_voz
EstudoAcessivel.atualizar_modulos = atualizar_modulos
EstudoAcessivel.setup_shortcuts = setup_shortcuts
EstudoAcessivel.setup_statusbar = setup_statusbar
EstudoAcessivel.switch_to_tab = switch_to_tab
EstudoAcessivel.on_tab_changed = on_tab_changed
EstudoAcessivel.show_help = show_help
EstudoAcessivel.closeEvent = closeEvent
EstudoAcessivel.changeEvent = changeEvent
