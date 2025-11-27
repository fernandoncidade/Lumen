from PySide6.QtGui import QShortcut, QKeySequence
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def setup_shortcuts(self):
    try:
        for i in range(5):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.tabs.setCurrentIndex(idx))

        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.show_help)

    except Exception as e:
        logger.critical(f"Erro crítico ao configurar atalhos: {str(e)}", exc_info=True)
        raise
