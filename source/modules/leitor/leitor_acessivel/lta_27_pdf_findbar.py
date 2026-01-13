from __future__ import annotations
from PySide6.QtCore import Qt, QCoreApplication, QObject, QEvent
from PySide6.QtGui import QKeySequence, QShortcut, QPalette
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox, QApplication
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


class PDFFindBar(QWidget):
    def __init__(self, owner, parent=None):
        super().__init__(parent)
        self.owner = owner

        self.setObjectName("PDFFindBar")
        self.setVisible(False)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(8)

        self.edt = QLineEdit()
        try:
            self.edt.setFrame(True)

            try:
                self.edt.clearMask()

            except Exception:
                rect = self.edt.rect()
                if not rect.isEmpty():
                    from PySide6.QtGui import QRegion
                    self.edt.setMask(QRegion(rect))

            self.edt.setAutoFillBackground(True)

        except Exception:
            pass

        self.edt.returnPressed.connect(self._on_enter_next)
        self.edt.textChanged.connect(lambda _: self._apply_search())

        try:
            fm = self.edt.fontMetrics()
            target_h = int(fm.height() * 1)
            self.edt.setMinimumHeight(max(24, target_h))

        except Exception:
            self.edt.setMinimumHeight(24)

        try:
            def _sync_edt_palette():
                try:
                    app = QApplication.instance()
                    if app is None:
                        return

                    window_color = app.palette().color(QPalette.Window)
                    base_color = app.palette().color(QPalette.Base)

                    try:
                        is_dark = int(window_color.lightness()) < 128

                    except Exception:
                        is_dark = False

                    if is_dark:
                        bg_color = base_color.darker(120)

                    else:
                        bg_color = window_color.darker(103)

                    pal = self.edt.palette()
                    pal.setColor(QPalette.Base, bg_color)
                    pal.setColor(QPalette.Text, app.palette().color(QPalette.Text))
                    pal.setColor(QPalette.Highlight, app.palette().color(QPalette.Highlight))
                    pal.setColor(QPalette.HighlightedText, app.palette().color(QPalette.HighlightedText))

                    try:
                        pal.setColor(QPalette.PlaceholderText, app.palette().color(QPalette.PlaceholderText))

                    except Exception:
                        pass

                    self.edt.setPalette(pal)

                except Exception as e:
                    logger.debug(f"Falha ao sincronizar paleta do campo de busca (PDF): {e}", exc_info=True)

            class _FindBarPaletteSyncFilter(QObject):
                def __init__(self, owner, sync_func):
                    super().__init__(owner)
                    self._sync_func = sync_func

                def eventFilter(self, obj, event):
                    try:
                        tipos = (
                            QEvent.ApplicationPaletteChange,
                            QEvent.PaletteChange,
                            QEvent.StyleChange,
                            QEvent.ThemeChange,
                        )
                        try:
                            tipos = tipos + (QEvent.ColorSchemeChange,)

                        except AttributeError:
                            pass

                        if event.type() in tipos:
                            self._sync_func()

                    except Exception:
                        pass

                    return super().eventFilter(obj, event)

            _sync_edt_palette()

            try:
                self._findbar_palette_sync_filter = _FindBarPaletteSyncFilter(self, _sync_edt_palette)
                app = QApplication.instance()
                if app is not None:
                    app.installEventFilter(self._findbar_palette_sync_filter)

            except Exception as e:
                logger.debug(f"Falha ao instalar filtro de paleta no PDFFindBar: {e}", exc_info=True)

        except Exception:
            pass

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
            self.edt.setPlaceholderText(QCoreApplication.translate("App", "Buscar no PDF..."))

            self.btn_prev.setToolTip(QCoreApplication.translate("App", "Anterior (Shift+Enter / Shift+F3)"))
            self.btn_next.setToolTip(QCoreApplication.translate("App", "Próximo (Enter / F3)"))

            self.chk_case.setText(QCoreApplication.translate("App", "Aa"))
            self.chk_case.setToolTip(QCoreApplication.translate("App", "Diferenciar maiúsculas/minúsculas"))

            self.chk_words.setText(QCoreApplication.translate("App", "Palavra"))
            self.chk_words.setToolTip(QCoreApplication.translate("App", "Somente palavra inteira"))

            self.chk_highlight.setText(QCoreApplication.translate("App", "Destacar tudo"))

            self.btn_close.setToolTip(QCoreApplication.translate("App", "Fechar (Esc)"))

        except Exception as e:
            logger.debug(f"Falha ao retranslate(PDFFindBar): {e}", exc_info=True)

    def show_bar(self):
        self.setVisible(True)
        self.edt.setFocus()
        self.edt.selectAll()
        self._apply_search()

    def hide_bar(self):
        try:
            self.setVisible(False)
            if self.owner and hasattr(self.owner, "_pdf_find_clear"):
                self.owner._pdf_find_clear()

        except Exception as e:
            logger.debug(f"Falha ao fechar PDFFindBar: {e}", exc_info=True)

    def update_count(self, cur: int, total: int):
        self.lbl_count.setText(f"{cur}/{total}")

    def _on_enter_next(self):
        mods = Qt.KeyboardModifier.NoModifier
        try:
            mods = QApplication.keyboardModifiers()

        except Exception:
            try:
                from PySide6.QtGui import QGuiApplication
                mods = QGuiApplication.queryKeyboardModifiers()

            except Exception:
                pass

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

            if hasattr(self.owner, "_pdf_find_apply"):
                self.owner._pdf_find_apply(q, match_case=match_case, whole_words=whole_words)

        except Exception as e:
            logger.debug(f"Falha _apply_search(PDF): {e}", exc_info=True)

    def _on_highlight_toggle(self, _):
        try:
            if self.owner and hasattr(self.owner, "_pdf_find_set_highlight_all"):
                self.owner._pdf_find_set_highlight_all(self.chk_highlight.isChecked())

        except Exception:
            pass

    def _call_owner_next(self):
        try:
            if self.owner and hasattr(self.owner, "_pdf_find_next"):
                self.owner._pdf_find_next()

        except Exception:
            pass

    def _call_owner_prev(self):
        try:
            if self.owner and hasattr(self.owner, "_pdf_find_prev"):
                self.owner._pdf_find_prev()

        except Exception:
            pass
