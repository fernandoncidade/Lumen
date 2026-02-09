from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QCursor
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def mouseMoveEvent(self, event):
    try:
        if self.resizing and self.resize_edge:
            delta = event.globalPos() - self.offset
            new_rect = QRect(self.start_geometry)

            if 'left' in self.resize_edge:
                new_rect.setLeft(self.start_geometry.left() + delta.x())

            if 'right' in self.resize_edge:
                new_rect.setRight(self.start_geometry.right() + delta.x())

            if 'top' in self.resize_edge:
                new_rect.setTop(self.start_geometry.top() + delta.y())

            if 'bottom' in self.resize_edge:
                new_rect.setBottom(self.start_geometry.bottom() + delta.y())

            min_width = 100
            min_height = 30

            if new_rect.width() < min_width:
                if 'left' in self.resize_edge:
                    new_rect.setLeft(new_rect.right() - min_width)

                else:
                    new_rect.setRight(new_rect.left() + min_width)

            if new_rect.height() < min_height:
                if 'top' in self.resize_edge:
                    new_rect.setTop(new_rect.bottom() - min_height)

                else:
                    new_rect.setBottom(new_rect.top() + min_height)

            self.setGeometry(new_rect)

        elif self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))
            self.setCursor(QCursor(Qt.ClosedHandCursor))

        else:
            self.update_cursor(event.pos())

    except Exception as e:
        logger.error(f"Erro ao processar movimento do mouse: {str(e)}", exc_info=True)
