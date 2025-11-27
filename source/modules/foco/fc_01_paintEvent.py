from PySide6.QtGui import QPainter, QColor
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def paintEvent(self, event):
    try:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 0, 50))
        painter.setPen(QColor(255, 200, 0, 200))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        painter.setBrush(QColor(255, 200, 0, 150))
        handle_size = 4
        if handle_size > 0:
            painter.drawEllipse(0, 0, handle_size, handle_size)
            painter.drawEllipse(self.width()-handle_size, 0, handle_size, handle_size)
            painter.drawEllipse(0, self.height()-handle_size, handle_size, handle_size)
            painter.drawEllipse(self.width()-handle_size, self.height()-handle_size, handle_size, handle_size)

        half_width = self.width() // 2
        half_height = self.height() // 2
        edge_size = 4

        if edge_size > 0:
            painter.drawRect(half_width - edge_size//2, 0, edge_size, edge_size)
            painter.drawRect(half_width - edge_size//2, self.height() - edge_size, edge_size, edge_size)
            painter.drawRect(0, half_height - edge_size//2, edge_size, edge_size)
            painter.drawRect(self.width() - edge_size, half_height - edge_size//2, edge_size, edge_size)

    except Exception as e:
        logger.error(f"Erro ao pintar Régua de Foco: {str(e)}", exc_info=True)
