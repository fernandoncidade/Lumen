from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPen
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def animate_focus_on(self, item):
    self.centerOn(item)
    eff_timer = QTimer(self)
    c = QColor(255, 255, 255, 60)
    pen = QPen(c, 3)
    item.setPen(pen)
    def restore():
        item.setPen(QPen(Qt.black, 2))

    eff_timer.singleShot(420, restore)
