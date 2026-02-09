from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _on_volume_changed(self, value: int):
    try:
        vol = max(0.0, min(1.0, value / 100.0))
        if hasattr(self, "audio_output") and self.audio_output is not None:
            self.audio_output.setVolume(vol)

        if not self.usar_edge_tts and self.tts_thread and getattr(self.tts_thread, "engine", None):
            try:
                self.tts_thread.engine.setProperty('volume', vol)

            except Exception:
                pass

    except Exception as e:
        logger.error(f"Erro ao ajustar volume: {str(e)}", exc_info=True)
