from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _on_speed_changed(self, value: int):
    try:
        rate = max(0.5, min(2.0, value / 150.0))

        if hasattr(self, "player") and self.player is not None:
            try:
                self.player.setPlaybackRate(rate)

            except Exception:
                pass

        if not self.usar_edge_tts and self.tts_thread and getattr(self.tts_thread, "engine", None):
            try:
                self.tts_thread.engine.setProperty('rate', int(value))

            except Exception:
                pass

    except Exception as e:
        logger.error(f"Erro ao ajustar velocidade: {str(e)}", exc_info=True)
