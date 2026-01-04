from __future__ import annotations
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


class TextFindBar(QWidget):
    def __init__(self, owner, parent=None):
        super().__init__(parent)
        self.owner = owner

        self.setObjectName("TextFindBar")
        self.setVisible(False)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(8)

        self.edt = QLineEdit()
        self.edt.returnPressed.connect(self._on_enter_next)
        self.edt.textChanged.connect(lambda _: self._apply_search())
        lay.addWidget(self.edt, 2)

        self.btn_prev = QPushButton("🔼")
        self.btn_prev.clicked.connect(self._call_owner_prev)
        lay.addWidget(self.btn_prev)

        self.btn_next = QPushButton("🔽")
        self.btn_next.clicked.connect(self._call_owner_next)
        lay.addWidget(self.btn_next)

        self.lbl_count = QLabel("0/0")
        self.lbl_count.setMinimumWidth(60)
        lay.addWidget(self.lbl_count)

        self.chk_case = QCheckBox()
        self.chk_case.stateChanged.connect(lambda _: self._apply_search())
        lay.addWidget(self.chk_case)

        self.chk_words = QCheckBox()
        self.chk_words.stateChanged.connect(lambda _: self._apply_search())
        lay.addWidget(self.chk_words)

        self.chk_highlight = QCheckBox()
        self.chk_highlight.setChecked(True)
        self.chk_highlight.stateChanged.connect(self._on_highlight_toggle)
        lay.addWidget(self.chk_highlight)

        lay.addStretch(1)

        self.btn_close = QPushButton("❌")
        self.btn_close.clicked.connect(self.hide_bar)
        lay.addWidget(self.btn_close)

        self._sc_esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self._sc_esc.activated.connect(self.hide_bar)

        self._sc_f3 = QShortcut(QKeySequence(Qt.Key.Key_F3), self)
        self._sc_f3.activated.connect(self._call_owner_next)

        self._sc_shift_f3 = QShortcut(QKeySequence("Shift+F3"), self)
        self._sc_shift_f3.activated.connect(self._call_owner_prev)

        self.retranslate()

    def retranslate(self):
        try:
            self.edt.setPlaceholderText(QCoreApplication.translate("App", "Buscar no Texto..."))

            self.btn_prev.setToolTip(QCoreApplication.translate("App", "Anterior (Shift+Enter / Shift+F3)"))
            self.btn_next.setToolTip(QCoreApplication.translate("App", "Próximo (Enter / F3)"))

            self.chk_case.setText(QCoreApplication.translate("App", "Aa"))
            self.chk_case.setToolTip(QCoreApplication.translate("App", "Diferenciar maiúsculas/minúsculas"))

            self.chk_words.setText(QCoreApplication.translate("App", "Palavra"))
            self.chk_words.setToolTip(QCoreApplication.translate("App", "Somente palavra inteira"))

            self.chk_highlight.setText(QCoreApplication.translate("App", "Destacar tudo"))

            self.btn_close.setToolTip(QCoreApplication.translate("App", "Fechar (Esc)"))

        except Exception as e:
            logger.debug(f"Falha ao retranslate(TextFindBar): {e}", exc_info=True)

    def show_bar(self):
        self.setVisible(True)
        self.edt.setFocus()
        self.edt.selectAll()
        self._apply_search()

    def hide_bar(self):
        try:
            self.setVisible(False)
            if self.owner and hasattr(self.owner, "_text_find_clear"):
                self.owner._text_find_clear()

        except Exception as e:
            logger.debug(f"Falha ao fechar TextFindBar: {e}", exc_info=True)

    def update_count(self, cur: int, total: int):
        self.lbl_count.setText(f"{cur}/{total}")

    def _on_enter_next(self):
        mods = self.edt.keyboardModifiers()
        if mods & Qt.KeyboardModifier.ShiftModifier:
            self._call_owner_prev()

        else:
            self._call_owner_next()

    def _apply_search(self):
        try:
            if not self.owner:
                return

            q = (self.edt.text() or "").strip()
            match_case = self.chk_case.isChecked()
            whole_words = self.chk_words.isChecked()

            if hasattr(self.owner, "_text_find_apply"):
                self.owner._text_find_apply(q, match_case=match_case, whole_words=whole_words)

        except Exception as e:
            logger.debug(f"Falha _apply_search(Text): {e}", exc_info=True)

    def _on_highlight_toggle(self, _):
        try:
            if self.owner and hasattr(self.owner, "_text_find_set_highlight_all"):
                self.owner._text_find_set_highlight_all(self.chk_highlight.isChecked())

        except Exception:
            pass

    def _call_owner_next(self):
        try:
            if self.owner and hasattr(self.owner, "_text_find_next"):
                self.owner._text_find_next()

        except Exception:
            pass

    def _call_owner_prev(self):
        try:
            if self.owner and hasattr(self.owner, "_text_find_prev"):
                self.owner._text_find_prev()

        except Exception:
            pass
