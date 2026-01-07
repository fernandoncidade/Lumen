from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def setup_shortcuts(self):
    try:
        for i in range(5):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.setContext(Qt.ApplicationShortcut)
            shortcut.activated.connect(lambda idx=i: self.tabs.setCurrentIndex(idx))

        help_seq = "F1"
        if not hasattr(self, 'action_atalhos'):
            help_shortcut = QShortcut(QKeySequence(help_seq), self)
            help_shortcut.setContext(Qt.ApplicationShortcut)
            help_shortcut.activated.connect(self.show_help)

        else:
            try:
                self.action_atalhos.setShortcut(help_seq)
                self.action_atalhos.setShortcutContext(Qt.ApplicationShortcut)

            except Exception:
                pass

    except Exception as e:
        logger.critical(f"Erro crítico ao configurar atalhos: {str(e)}", exc_info=True)
        raise
