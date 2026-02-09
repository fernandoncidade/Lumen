from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def mousePressEvent(self, event):
    try:
        if event.button() == Qt.LeftButton:
            self.resize_edge = self.get_resize_edge(event.pos())

            if self.resize_edge:
                self.resizing = True
                self.offset = event.globalPos()
                self.start_geometry = self.geometry()

            else:
                self.dragging = True
                self.offset = event.pos()
                self.setCursor(QCursor(Qt.ClosedHandCursor))

    except Exception as e:
        logger.error(f"Erro ao processar clique do mouse: {str(e)}", exc_info=True)
