from .lta_01_setup_ui import setup_ui
from .lta_02_atualizar_traducoes import atualizar_traducoes
from .lta_03_update_pause_button import _update_pause_button
from .lta_04_ajustar_fonte import ajustar_fonte
from .lta_05_carregar_pdf import carregar_pdf
from .lta_06_iniciar_leitura import iniciar_leitura
from .lta_07_pausar_leitura import pausar_leitura
from .lta_08_parar_leitura import parar_leitura
from .lta_09_play_generated_audio import _play_generated_audio
from .lta_10_on_media_status import _on_media_status
from .lta_11_on_tts_error import _on_tts_error
from .lta_12_on_volume_changed import _on_volume_changed
from .lta_13_on_speed_changed import _on_speed_changed
from .lta_14_leitura_finalizada import leitura_finalizada
from .lta_15_toggle_regua_foco import toggle_regua_foco
from .lta_16_ativar_regua_foco import ativar_regua_foco
from .lta_17_desativar_regua_foco import desativar_regua_foco
from .lta_18_regua_fechada import regua_fechada
from .lta_19_cleanup import cleanup
from .lta_20_definir_voz import definir_voz
from .lta_21_atualizar_fonte_persistente import atualizar_fonte_persistente
from .lta_22_pdf_toolbar import (
    setup_pdf_toolbar,
    _pdf_goto_page,
    _pdf_next_page,
    _pdf_prev_page,
    _pdf_zoom_in,
    _pdf_zoom_out,
    _pdf_zoom_fit_width,
    _pdf_zoom_fit_page,
    _pdf_set_hand_mode,
    _pdf_set_selection_mode,
    _pdf_enable_toolbar,
)
from .lta_23_pdf_mouse_handler import PDFMouseHandler
from .lta_24_text_tools import (
    criar_texto,
    salvar_como,
    toggle_bullets,
    set_line_spacing,
    set_indent,
    set_margins,
)

__all__ = [
    "setup_ui",
    "atualizar_traducoes",
    "_update_pause_button",
    "ajustar_fonte",
    "carregar_pdf",
    "iniciar_leitura",
    "pausar_leitura",
    "parar_leitura",
    "_play_generated_audio",
    "_on_media_status",
    "_on_tts_error",
    "_on_volume_changed",
    "_on_speed_changed",
    "leitura_finalizada",
    "toggle_regua_foco",
    "ativar_regua_foco",
    "desativar_regua_foco",
    "regua_fechada",
    "cleanup",
    "definir_voz",
    "atualizar_fonte_persistente",
    "setup_pdf_toolbar",
    "_pdf_goto_page",
    "_pdf_next_page",
    "_pdf_prev_page",
    "_pdf_zoom_in",
    "_pdf_zoom_out",
    "_pdf_zoom_fit_width",
    "_pdf_zoom_fit_page",
    "_pdf_set_hand_mode",
    "_pdf_set_selection_mode",
    "_pdf_enable_toolbar",
    "PDFMouseHandler",
    "criar_texto",
    "salvar_como",
    "toggle_bullets",
    "set_line_spacing",
    "set_indent",
    "set_margins",
]
