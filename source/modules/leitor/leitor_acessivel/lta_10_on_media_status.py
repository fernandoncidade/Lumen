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

            prev = getattr(self, "_current_generated", None)
            if prev and os.path.exists(prev):
                try:
                    os.remove(prev)
                    if getattr(self, "_generated_files", None) and prev in self._generated_files:
                        try:
                            self._generated_files.remove(prev)

                        except Exception as e:
                            logger.debug(f"Falha ao remover último chunk da lista: {prev}", exc_info=True)

                except Exception as e:
                    logger.debug(f"Não foi possível remover último chunk: {prev}", exc_info=True)

            try:
                self._generated_queue = []
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
