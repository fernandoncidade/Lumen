from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def mouseReleaseEvent(self, event):
    try:
        if self.dragging:
            edge = self.get_resize_edge(event.pos())
            if edge is None:
                self.setCursor(QCursor(Qt.OpenHandCursor))

            else:
                self.update_cursor(event.pos())

        self.dragging = False
        self.resizing = False
        self.resize_edge = None

    except Exception as e:
        logger.error(f"Erro ao processar liberação do mouse: {str(e)}", exc_info=True)
