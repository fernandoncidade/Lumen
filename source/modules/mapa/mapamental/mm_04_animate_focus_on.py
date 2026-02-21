from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPen
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def animate_focus_on(self, item):
    self.centerOn(item)

    timer = QTimer(self)
    timer.setSingleShot(True)

    c = QColor(255, 255, 255, 60)
    pen = QPen(c, 3)
    item.setPen(pen)

    if not hasattr(self, "_lumen_focus_timers"):
        self._lumen_focus_timers = []

    self._lumen_focus_timers.append(timer)

    def restore():
        try:
            item.setPen(QPen(Qt.black, 2))

        finally:
            try:
                self._lumen_focus_timers.remove(timer)

            except Exception:
                pass

    timer.timeout.connect(restore)
    timer.start(420)
