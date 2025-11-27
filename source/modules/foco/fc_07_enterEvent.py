from PySide6.QtGui import QCursor
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def enterEvent(self, event):
    try:
        self.update_cursor(self.mapFromGlobal(QCursor.pos()))

    except Exception as e:
        logger.error(f"Erro ao processar entrada do cursor: {str(e)}", exc_info=True)
