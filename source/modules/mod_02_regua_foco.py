from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPoint
from source.utils.LogManager import LogManager
from source.modules.foco import (
    paintEvent,
    get_resize_edge,
    mousePressEvent,
    mouseMoveEvent,
    mouseReleaseEvent,
    keyPressEvent,
    enterEvent,
    update_cursor
)


class ReguaFoco(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = LogManager.get_logger()

        try:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAttribute(Qt.WA_DeleteOnClose, True)
            self.setGeometry(100, 100, 800, 80)
            self.dragging = False
            self.resizing = False
            self.offset = QPoint()
            self.resize_edge = None
            self.resize_margin = 15

            self.setMouseTracking(True)

        except Exception as e:
            self.logger.error(f"Erro ao inicializar Régua de Foco: {str(e)}", exc_info=True)

    def paintEvent(self, event):
        paintEvent(self, event)

    def get_resize_edge(self, pos):
        return get_resize_edge(self, pos)

    def mousePressEvent(self, event):
        mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        keyPressEvent(self, event)

    def enterEvent(self, event):
        enterEvent(self, event)

    def update_cursor(self, pos):
        update_cursor(self, pos)

