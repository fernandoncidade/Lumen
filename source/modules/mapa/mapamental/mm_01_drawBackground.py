from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QLinearGradient
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def drawBackground(self, painter: QPainter, rect: QRectF):
    try:
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor("#121212"))
        grad.setColorAt(0.5, QColor(25, 25, 25))
        grad.setColorAt(1.0, QColor("#1e1e1e"))
        painter.fillRect(rect, grad)

        left = int(rect.left()) - (int(rect.left()) % self._grid_step)
        top = int(rect.top()) - (int(rect.top()) % self._grid_step)

        painter.setPen(self._grid_pen_light)
        for x in range(left, int(rect.right()), self._grid_step):
            painter.drawLine(x, rect.top(), x, rect.bottom())

        for y in range(top, int(rect.bottom()), self._grid_step):
            painter.drawLine(rect.left(), y, rect.right(), y)

        painter.setPen(self._grid_pen_dark)
        strong = self._grid_step * 5
        left_s = int(rect.left()) - (int(rect.left()) % strong)
        top_s = int(rect.top()) - (int(rect.top()) % strong)
        for x in range(left_s, int(rect.right()), strong):
            painter.drawLine(x, rect.top(), x, rect.bottom())

        for y in range(top_s, int(rect.bottom()), strong):
            painter.drawLine(rect.left(), y, rect.right(), y)

    except Exception as e:
        logger.error(f"Erro ao desenhar o fundo: {e}", exc_info=True)
