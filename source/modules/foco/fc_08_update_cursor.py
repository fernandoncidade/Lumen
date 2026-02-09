from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def update_cursor(self, pos):
    try:
        edge = self.get_resize_edge(pos)

        if edge in ['top-left', 'bottom-right']:
            self.setCursor(QCursor(Qt.SizeFDiagCursor))

        elif edge in ['top-right', 'bottom-left']:
            self.setCursor(QCursor(Qt.SizeBDiagCursor))

        elif edge in ['left', 'right']:
            self.setCursor(QCursor(Qt.SizeHorCursor))

        elif edge in ['top', 'bottom']:
            self.setCursor(QCursor(Qt.SizeVerCursor))

        else:
            self.setCursor(QCursor(Qt.OpenHandCursor))

    except Exception as e:
        logger.error(f"Erro ao atualizar cursor: {str(e)}", exc_info=True)
