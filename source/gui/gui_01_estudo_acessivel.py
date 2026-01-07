import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication
from source.language.tr_01_gerenciadorTraducao import GerenciadorTraducao
from source.utils.LogManager import LogManager
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
    def __init__(
        self,
        only_module_ids=None,
        detached: bool = False,
        detached_origin=None,
        provided_tabs=None,
        detached_module_id: str | None = None,
        detached_origin_index: int | None = None,
        detached_title: str | None = None,
        detached_widget=None,
    ):
        super().__init__()
        try:
            self.only_module_ids = only_module_ids
            self.detached = detached
            self.detached_origin = detached_origin
            self.provided_tabs = provided_tabs or {}

            self.detached_module_id = detached_module_id
            self.detached_origin_index = detached_origin_index
            self.detached_title = detached_title
            self.detached_widget = detached_widget
            self.detached_reattached = False

            try:
                from source.gui.gui_03_events import EventBus
                from source.gui.gui_02_interfaces import ModuleContext
                from PySide6.QtWidgets import QApplication
                self.event_bus = EventBus()
                self._module_context = ModuleContext(event_bus=self.event_bus, app=QApplication.instance(), host=self)

            except Exception:
                self.event_bus = None
                self._module_context = None

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
                if icon_path and os.path.exists(icon_path):
                    window_icon = QIcon(icon_path)
                    self.setWindowIcon(window_icon)
                    logger.debug(f"Ícone da janela configurado: {icon_path}")

                else:
                    logger.warning(f"Caminho do ícone 'autismo.ico' não encontrado ou inválido: {icon_path}")

            except Exception as e:
                logger.error(f"Erro ao carregar ícone da janela: {e}", exc_info=True)

        except Exception as e:
            logger.critical(f"Erro crítico ao inicializar EstudoAcessivelApp: {str(e)}", exc_info=True)
            raise

from source.gui.ui import (
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
    changeEvent,
    detach_module_tab,
    _reattach_module_tab
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
EstudoAcessivel.detach_module_tab = detach_module_tab
EstudoAcessivel._reattach_module_tab = _reattach_module_tab
