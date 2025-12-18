from PySide6.QtCore import QPointF
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def snap(self, pos: QPointF) -> QPointF:
    try:
        if not self._snap_enabled:
            return pos

        step = self._grid_step
        return QPointF(round(pos.x() / step) * step, round(pos.y() / step) * step)

    except Exception as e:
        logger.error(f"Erro ao aplicar snap: {e}", exc_info=True)
        return pos
