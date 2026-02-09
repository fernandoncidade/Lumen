from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def cleanup(self):
    try:
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.stop()
            self.tts_thread.wait(2000)
            if self.tts_thread.isRunning():
                self.tts_thread.terminate()
                self.tts_thread.wait()

        if self.regua is not None:
            self.regua.close()
            self.regua = None

    except Exception as e:
        logger.error(f"Erro ao limpar recursos do Leitor Acessível: {str(e)}", exc_info=True)
