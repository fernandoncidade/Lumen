from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def keyPressEvent(self, event):
    try:
        resize_increment = 5
        move_increment = 5
        
        if event.key() == Qt.Key_Escape:
            self.close()

        elif event.key() == Qt.Key_Up:
            self.setGeometry(self.x(), self.y(), self.width(), max(30, self.height() - resize_increment))

        elif event.key() == Qt.Key_Down:
            self.setGeometry(self.x(), self.y(), self.width(), self.height() + resize_increment)

        elif event.key() == Qt.Key_Left:
            self.setGeometry(self.x(), self.y(), max(100, self.width() - resize_increment*2), self.height())

        elif event.key() == Qt.Key_Right:
            self.setGeometry(self.x(), self.y(), self.width() + resize_increment*2, self.height())

        elif event.key() == Qt.Key_W:
            self.setGeometry(self.x(), self.y() - move_increment, self.width(), self.height())

        elif event.key() == Qt.Key_S:
            self.setGeometry(self.x(), self.y() + move_increment, self.width(), self.height())

        elif event.key() == Qt.Key_A:
            self.setGeometry(self.x() - move_increment, self.y(), self.width(), self.height())

        elif event.key() == Qt.Key_D:
            self.setGeometry(self.x() + move_increment, self.y(), self.width(), self.height())

    except Exception as e:
        logger.error(f"Erro ao processar tecla pressionada: {str(e)}", exc_info=True)
