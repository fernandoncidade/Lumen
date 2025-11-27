from source.utils.LogManager import LogManager
from PySide6.QtWidgets import QMainWindow

logger = LogManager.get_logger()

def changeEvent(self, event):
    if event.type() == event.Type.LanguageChange:
        self.atualizar_interface(self.tradutor.obter_idioma_atual())

    QMainWindow.changeEvent(self, event)
