from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def leitura_finalizada(self):
    try:
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self._is_paused = False
        self._update_pause_button()
        self.btn_pause.setChecked(False)
        if self.btn_stop is not None:
            self.btn_stop.setEnabled(False)

        self._stop_speech_highlight()
        self._stop_pdf_speech_highlight()

    except Exception as e:
        logger.error(f"Erro ao finalizar leitura: {str(e)}", exc_info=True)
