from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import QUrl
from source.utils.LogManager import LogManager
import os

logger = LogManager.get_logger()

def _on_media_status(self, status):
    try:
        if status == QMediaPlayer.EndOfMedia:
            try:
                prev = getattr(self, "_current_generated", None)

                if getattr(self, "_generated_queue", None):
                    next_path = self._generated_queue.pop(0)
                    self._current_generated = next_path
                    self.player.setSource(QUrl.fromLocalFile(next_path))
                    self.player.play()
                    if prev and os.path.exists(prev):
                        try:
                            os.remove(prev)
                            if getattr(self, "_generated_files", None) and prev in self._generated_files:
                                try:
                                    self._generated_files.remove(prev)

                                except Exception as e:
                                    logger.debug(f"Falha ao remover chunk anterior da lista: {prev}", exc_info=True)

                        except Exception as e:
                            logger.debug(f"Não foi possível remover chunk anterior: {prev}", exc_info=True)

                    return

            except Exception as e:
                logger.error(f"Erro ao tocar próximo chunk: {e}", exc_info=True)

            try:
                if hasattr(self, "player") and self.player is not None:
                    try:
                        self.player.stop()

                    except Exception:
                        pass

                    try:
                        self.player.setSource(QUrl())

                    except Exception:
                        pass

            except Exception:
                pass

            try:
                from .lta_25_audio_temp_cleanup import cleanup_paths_with_retry, cleanup_edge_tts_temp_in_outdir

                files = list(getattr(self, "_generated_files", []) or [])
                queue = list(getattr(self, "_generated_queue", []) or [])
                current = getattr(self, "_current_generated", None)

                targets = []
                targets.extend(files)
                targets.extend(queue)
                if current:
                    targets.append(current)

                cleanup_paths_with_retry(self, targets)
                cleanup_edge_tts_temp_in_outdir(self, remove_mp3=True, remove_part=True)

            except Exception as e:
                logger.debug(f"Falha ao executar limpeza final com retry: {e}", exc_info=True)

            try:
                self._generated_queue = []
                self._generated_files = []
                self._current_generated = None

            except Exception as e:
                logger.debug(f"Erro ao limpar estado da fila: {e}", exc_info=True)

            self.leitura_finalizada()

        elif status == QMediaPlayer.InvalidMedia:
            cur = getattr(self, "_current_generated", None)
            if cur and os.path.exists(cur):
                try:
                    os.remove(cur)
                    if getattr(self, "_generated_files", None) and cur in self._generated_files:
                        try:
                            self._generated_files.remove(cur)

                        except Exception as e:
                            logger.debug(f"Falha ao remover mídia inválida da lista: {cur}", exc_info=True)

                except Exception as e:
                    logger.debug(f"Não foi possível remover mídia inválida: {cur}", exc_info=True)

            self._generated_queue = []
            self._current_generated = None
            self.leitura_finalizada()

    except Exception as e:
        logger.error(f"Erro no status do player: {str(e)}", exc_info=True)
