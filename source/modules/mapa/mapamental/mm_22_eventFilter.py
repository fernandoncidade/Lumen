from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QWidget
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def eventFilter(self, obj, event):
    try:
        tipos = (QEvent.ApplicationPaletteChange, QEvent.PaletteChange, QEvent.StyleChange,)

        try:
            tipos = tipos + (QEvent.ThemeChange,)

        except AttributeError:
            pass

        try:
            tipos = tipos + (QEvent.ColorSchemeChange,)

        except AttributeError:
            pass

        if event.type() in tipos:
            self.atualizar_tema()

    except Exception as e:
        logger.error(f"Erro no eventFilter de tema: {str(e)}", exc_info=True)

    return QWidget.eventFilter(self, obj, event)
