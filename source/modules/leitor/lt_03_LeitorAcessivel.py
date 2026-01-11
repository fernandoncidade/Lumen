from PySide6.QtWidgets import QWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from source.utils.LogManager import LogManager
from source.utils.GerenciadorBotoesUI import GerenciadorBotoesUI


class LeitorAcessivel(QWidget):
    def __init__(self):
        super().__init__()
        self.tts_thread = None
        self.regua = None
        self.voz_id_atual = None
        self.logger = LogManager.get_logger()
        self.gerenciador_botoes = GerenciadorBotoesUI(self)
        self.usar_edge_tts = True
        self._is_paused = False
        self.btn_stop = None

        self.pdf_view = None
        self.pdf_doc = None
        self._pdf_mouse_handler = None
        self._pdf_toolbar_widgets = []

        self.setup_ui()

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)

        self._generated_queue = []
        self._current_generated = None
        self._generated_files = []

        try:
            self.audio_output.setVolume(self.slider_volume.value() / 100.0)

        except Exception:
            pass

        self.player.mediaStatusChanged.connect(self._on_media_status)

from source.modules.leitor.leitor_acessivel import (
    setup_ui,
    atualizar_traducoes,
    _update_pause_button,
    ajustar_fonte,
    carregar_pdf,
    iniciar_leitura,
    pausar_leitura,
    parar_leitura,
    _play_generated_audio,
    _on_media_status,
    _on_tts_error,
    _on_volume_changed,
    _on_speed_changed,
    leitura_finalizada,
    toggle_regua_foco,
    ativar_regua_foco,
    desativar_regua_foco,
    regua_fechada,
    cleanup,
    definir_voz,
    atualizar_fonte_persistente,
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
    PDFMouseHandler,
    criar_texto,
    salvar_como,
    toggle_bullets,
    set_line_spacing,
    set_indent,
    set_margins,
    _pdf_find_show,
    _pdf_find_clear,
    _pdf_find_apply,
    _pdf_find_next,
    _pdf_find_prev,
    _pdf_find_set_highlight_all,
    _pdf_update_page_ui,
    TextFindBar,
    _text_find_show,
    _text_find_clear,
    _text_find_apply,
    _text_find_next,
    _text_find_prev,
    _text_find_goto_hit,
    _text_find_apply_highlights,
    _text_find_set_highlight_all,
    _pdf_find_toggle,
    _text_find_toggle,
    _init_speech_highlight,
    _setup_speech_highlight_for_reading,
    _on_timestamps_received,
    _start_speech_highlight,
    _pause_speech_highlight,
    _resume_speech_highlight,
    _stop_speech_highlight,
    toggle_speech_highlight,
    set_speech_highlight_mode,
    set_speech_highlight_style,
    set_speech_highlight_auto_scroll,
    is_speech_highlight_enabled,
    _on_toggle_leitura_assistida,
    _on_modo_leitura_changed,
    _update_leitura_assistida_button,
    _init_leitura_assistida_state,
    _notify_chunk_changed,
    _notify_pdf_chunk_changed,
    _init_pdf_speech_highlight,
    _setup_pdf_speech_highlight_for_reading,
    _on_pdf_timestamps_received,
    _start_pdf_speech_highlight,
    _pause_pdf_speech_highlight,
    _resume_pdf_speech_highlight,
    _stop_pdf_speech_highlight,
    toggle_pdf_speech_highlight,
    set_pdf_speech_highlight_mode,
    is_pdf_speech_highlight_enabled,
)

LeitorAcessivel.setup_ui = setup_ui
LeitorAcessivel.atualizar_traducoes = atualizar_traducoes
LeitorAcessivel._update_pause_button = _update_pause_button
LeitorAcessivel.ajustar_fonte = ajustar_fonte
LeitorAcessivel.carregar_pdf = carregar_pdf
LeitorAcessivel.iniciar_leitura = iniciar_leitura
LeitorAcessivel.pausar_leitura = pausar_leitura
LeitorAcessivel.parar_leitura = parar_leitura
LeitorAcessivel._play_generated_audio = _play_generated_audio
LeitorAcessivel._on_media_status = _on_media_status
LeitorAcessivel._on_tts_error = _on_tts_error
LeitorAcessivel._on_volume_changed = _on_volume_changed
LeitorAcessivel._on_speed_changed = _on_speed_changed
LeitorAcessivel.leitura_finalizada = leitura_finalizada
LeitorAcessivel.toggle_regua_foco = toggle_regua_foco
LeitorAcessivel.ativar_regua_foco = ativar_regua_foco
LeitorAcessivel.desativar_regua_foco = desativar_regua_foco
LeitorAcessivel.regua_fechada = regua_fechada
LeitorAcessivel.cleanup = cleanup
LeitorAcessivel.definir_voz = definir_voz
LeitorAcessivel.atualizar_fonte_persistente = atualizar_fonte_persistente
LeitorAcessivel.setup_pdf_toolbar = setup_pdf_toolbar
LeitorAcessivel._pdf_goto_page = _pdf_goto_page
LeitorAcessivel._pdf_next_page = _pdf_next_page
LeitorAcessivel._pdf_prev_page = _pdf_prev_page
LeitorAcessivel._pdf_zoom_in = _pdf_zoom_in
LeitorAcessivel._pdf_zoom_out = _pdf_zoom_out
LeitorAcessivel._pdf_zoom_fit_width = _pdf_zoom_fit_width
LeitorAcessivel._pdf_zoom_fit_page = _pdf_zoom_fit_page
LeitorAcessivel._pdf_set_hand_mode = _pdf_set_hand_mode
LeitorAcessivel._pdf_set_selection_mode = _pdf_set_selection_mode
LeitorAcessivel._pdf_enable_toolbar = _pdf_enable_toolbar
LeitorAcessivel.PDFMouseHandler = PDFMouseHandler
LeitorAcessivel.criar_texto = criar_texto
LeitorAcessivel.salvar_como = salvar_como
LeitorAcessivel.toggle_bullets = toggle_bullets
LeitorAcessivel.set_line_spacing = set_line_spacing
LeitorAcessivel.set_indent = set_indent
LeitorAcessivel.set_margins = set_margins
LeitorAcessivel._pdf_find_show = _pdf_find_show
LeitorAcessivel._pdf_find_clear = _pdf_find_clear
LeitorAcessivel._pdf_find_apply = _pdf_find_apply
LeitorAcessivel._pdf_find_next = _pdf_find_next
LeitorAcessivel._pdf_find_prev = _pdf_find_prev
LeitorAcessivel._pdf_find_set_highlight_all = _pdf_find_set_highlight_all
LeitorAcessivel._pdf_update_page_ui = _pdf_update_page_ui
LeitorAcessivel.TextFindBar = TextFindBar
LeitorAcessivel._text_find_show = _text_find_show
LeitorAcessivel._text_find_clear = _text_find_clear
LeitorAcessivel._text_find_apply = _text_find_apply
LeitorAcessivel._text_find_next = _text_find_next
LeitorAcessivel._text_find_prev = _text_find_prev
LeitorAcessivel._text_find_goto_hit = _text_find_goto_hit
LeitorAcessivel._text_find_apply_highlights = _text_find_apply_highlights
LeitorAcessivel._text_find_set_highlight_all = _text_find_set_highlight_all
LeitorAcessivel._pdf_find_toggle = _pdf_find_toggle
LeitorAcessivel._text_find_toggle = _text_find_toggle
LeitorAcessivel._init_speech_highlight = _init_speech_highlight
LeitorAcessivel._setup_speech_highlight_for_reading = _setup_speech_highlight_for_reading
LeitorAcessivel._on_timestamps_received = _on_timestamps_received
LeitorAcessivel._start_speech_highlight = _start_speech_highlight
LeitorAcessivel._pause_speech_highlight = _pause_speech_highlight
LeitorAcessivel._resume_speech_highlight = _resume_speech_highlight
LeitorAcessivel._stop_speech_highlight = _stop_speech_highlight
LeitorAcessivel.toggle_speech_highlight = toggle_speech_highlight
LeitorAcessivel.set_speech_highlight_mode = set_speech_highlight_mode
LeitorAcessivel.set_speech_highlight_style = set_speech_highlight_style
LeitorAcessivel.set_speech_highlight_auto_scroll = set_speech_highlight_auto_scroll
LeitorAcessivel.is_speech_highlight_enabled = is_speech_highlight_enabled
LeitorAcessivel._on_toggle_leitura_assistida = _on_toggle_leitura_assistida
LeitorAcessivel._on_modo_leitura_changed = _on_modo_leitura_changed
LeitorAcessivel._update_leitura_assistida_button = _update_leitura_assistida_button
LeitorAcessivel._init_leitura_assistida_state = _init_leitura_assistida_state
LeitorAcessivel._notify_chunk_changed = _notify_chunk_changed
LeitorAcessivel._notify_pdf_chunk_changed = _notify_pdf_chunk_changed
LeitorAcessivel._init_pdf_speech_highlight = _init_pdf_speech_highlight
LeitorAcessivel._setup_pdf_speech_highlight_for_reading = _setup_pdf_speech_highlight_for_reading
LeitorAcessivel._on_pdf_timestamps_received = _on_pdf_timestamps_received
LeitorAcessivel._start_pdf_speech_highlight = _start_pdf_speech_highlight
LeitorAcessivel._pause_pdf_speech_highlight = _pause_pdf_speech_highlight
LeitorAcessivel._resume_pdf_speech_highlight = _resume_pdf_speech_highlight
LeitorAcessivel._stop_pdf_speech_highlight = _stop_pdf_speech_highlight
LeitorAcessivel.toggle_pdf_speech_highlight = toggle_pdf_speech_highlight
LeitorAcessivel.set_pdf_speech_highlight_mode = set_pdf_speech_highlight_mode
LeitorAcessivel.is_pdf_speech_highlight_enabled = is_pdf_speech_highlight_enabled
