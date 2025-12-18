from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def wheelEvent(self, event):
    zoom_in_factor = 1.15
    zoom_out_factor = 1 / zoom_in_factor
    if event.angleDelta().y() > 0:
        factor = zoom_in_factor
        self._current_zoom += 1

    else:
        factor = zoom_out_factor
        self._current_zoom -= 1

    if -15 <= self._current_zoom <= 25:
        self.scale(factor, factor)
