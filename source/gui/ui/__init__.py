from source.gui.ui.ui_01_setup_ui import setup_ui
from source.gui.ui.ui_02_sincronizar_regua_menu import sincronizar_regua_menu
from source.gui.ui.ui_03_setup_menubar import setup_menubar
from source.gui.ui.ui_04_executar_acao_modulo import executar_acao_modulo
from source.gui.ui.ui_05_mudar_idioma import mudar_idioma
from source.gui.ui.ui_06_exibir_sobre import exibir_sobre
from source.gui.ui.ui_07_atualizar_interface import atualizar_interface
from source.gui.ui.ui_08_atualizar_menu import atualizar_menu
from source.gui.ui.ui_09_get_persist_file import _get_persist_file
from source.gui.ui.ui_10_salvar_voz_persistente import _salvar_voz_persistente
from source.gui.ui.ui_11_carregar_voz_persistente import _carregar_voz_persistente
from source.gui.ui.ui_12_carregar_vozes import carregar_vozes
from source.gui.ui.ui_13_definir_voz import definir_voz
from source.gui.ui.ui_14_atualizar_modulos import atualizar_modulos
from source.gui.ui.ui_15_setup_shortcuts import setup_shortcuts
from source.gui.ui.ui_16_setup_statusbar import setup_statusbar
from source.gui.ui.ui_17_switch_to_tab import switch_to_tab
from source.gui.ui.ui_18_on_tab_changed import on_tab_changed
from source.gui.ui.ui_19_show_help import show_help
from source.gui.ui.ui_20_closeEvent import closeEvent
from source.gui.ui.ui_21_changeEvent import changeEvent
from source.gui.ui.ui_22_font_config_dialog import FontConfigDialog
from source.gui.ui.ui_24_detach_module_tab import detach_module_tab, _reattach_module_tab

__all__ = [
    "setup_ui",
    "sincronizar_regua_menu",
    "setup_menubar",
    "executar_acao_modulo",
    "mudar_idioma",
    "exibir_sobre",
    "atualizar_interface",
    "atualizar_menu",
    "_get_persist_file",
    "_salvar_voz_persistente",
    "_carregar_voz_persistente",
    "carregar_vozes",
    "definir_voz",
    "atualizar_modulos",
    "setup_shortcuts",
    "setup_statusbar",
    "switch_to_tab",
    "on_tab_changed",
    "show_help",
    "closeEvent",
    "changeEvent",
    "FontConfigDialog",
    "detach_module_tab",
    "_reattach_module_tab",
]
