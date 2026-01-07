from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QFontComboBox, QGroupBox, QFormLayout
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QFont, QPalette
from source.utils.FontManager import FontManager
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()


class FontConfigDialog(QDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle(QCoreApplication.translate("App", "Configuração de Fontes"))
            self.setModal(True)
            self.setGeometry(100, 100, 500, 300)
            self.tr = lambda s: QCoreApplication.translate("App", s)

            self.init_ui()
            self.load_config()
            self._update_preview_colors()

        except Exception as e:
            logger.error(f"Erro ao inicializar FontConfigDialog: {e}", exc_info=True)
            raise

    def init_ui(self):
        try:
            layout = QVBoxLayout(self)

            config_group = QGroupBox(self.tr("Configurações de Fonte"))
            form_layout = QFormLayout(config_group)

            self.font_combo = QFontComboBox()
            form_layout.addRow(self.tr("Família da Fonte:"), self.font_combo)

            self.size_spin = QSpinBox()
            self.size_spin.setMinimum(6)
            self.size_spin.setMaximum(24)
            self.size_spin.setValue(10)
            form_layout.addRow(self.tr("Tamanho:"), self.size_spin)

            self.bold_check = QCheckBox(self.tr("Negrito"))
            form_layout.addRow(self.bold_check)

            self.italic_check = QCheckBox(self.tr("Itálico"))
            form_layout.addRow(self.italic_check)

            self.underline_check = QCheckBox(self.tr("Sublinhado"))
            form_layout.addRow(self.underline_check)

            layout.addWidget(config_group)

            preview_group = QGroupBox(self.tr("Prévia"))
            preview_layout = QVBoxLayout(preview_group)
            self.preview_label = QLabel(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
                "abcdefghijklmnopqrstuvwxyz\n"
                "0123456789\n"
                "═══════════════════════════"
            )
            self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.preview_label.setStyleSheet("QLabel { padding: 8px; border: 1px solid palette(mid); }")
            preview_layout.addWidget(self.preview_label)
            layout.addWidget(preview_group)

            btn_layout = QHBoxLayout()

            btn_reset = QPushButton(self.tr("Padrão"))
            btn_reset.clicked.connect(self.reset_to_default)
            btn_layout.addWidget(btn_reset)

            btn_layout.addStretch()

            btn_ok = QPushButton(self.tr("OK"))
            btn_ok.clicked.connect(self.apply_and_close)
            btn_layout.addWidget(btn_ok)

            btn_cancel = QPushButton(self.tr("Cancelar"))
            btn_cancel.clicked.connect(self.reject)
            btn_layout.addWidget(btn_cancel)

            layout.addLayout(btn_layout)

            self.font_combo.currentFontChanged.connect(self.update_preview)
            self.size_spin.valueChanged.connect(self.update_preview)
            self.bold_check.stateChanged.connect(self.update_preview)
            self.italic_check.stateChanged.connect(self.update_preview)
            self.underline_check.stateChanged.connect(self.update_preview)

        except Exception as e:
            logger.error(f"Erro ao inicializar UI do FontConfigDialog: {e}", exc_info=True)
            raise

    def _get_text_color(self) -> str:
        try:
            palette = self.palette()
            text_color = palette.color(QPalette.WindowText)
            return text_color.name()

        except Exception as e:
            logger.error(f"Erro ao obter cor do texto: {e}")
            return "#000000"

    def _get_background_color(self) -> str:
        try:
            palette = self.palette()
            bg_color = palette.color(QPalette.Window)
            return bg_color.name()

        except Exception as e:
            logger.error(f"Erro ao obter cor de fundo: {e}")
            return "#ffffff"

    def _update_preview_colors(self):
        try:
            text_color = self._get_text_color()
            bg_color = self._get_background_color()

            self.preview_label.setStyleSheet(
                f"QLabel {{ "
                f"padding: 8px; "
                f"border: 1px solid palette(mid); "
                f"color: {text_color}; "
                f"background-color: {bg_color}; "
                f"}}"
            )

        except Exception as e:
            logger.error(f"Erro ao atualizar cores da prévia: {e}")

    def changeEvent(self, event):
        try:
            from PySide6.QtCore import QEvent
            if event.type() == QEvent.PaletteChange:
                self._update_preview_colors()
                self.update_preview()

            super().changeEvent(event)

        except Exception as e:
            logger.error(f"Erro em changeEvent: {e}")
            super().changeEvent(event)

    def load_config(self):
        try:
            config = FontManager.get_config()
            self.font_combo.setCurrentFont(QFont(config["family"]))
            self.size_spin.setValue(config["size"])
            self.bold_check.setChecked(config["bold"])
            self.italic_check.setChecked(config["italic"])
            self.underline_check.setChecked(config["underline"])
            self.update_preview()

        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}", exc_info=True)

    def update_preview(self):
        try:
            font = QFont(self.font_combo.currentFont().family(), self.size_spin.value())
            font.setBold(self.bold_check.isChecked())
            font.setItalic(self.italic_check.isChecked())
            font.setUnderline(self.underline_check.isChecked())
            self.preview_label.setFont(font)
            self._update_preview_colors()

        except Exception as e:
            logger.error(f"Erro ao atualizar prévia: {e}", exc_info=True)

    def get_config(self) -> dict:
        return {
            "family": self.font_combo.currentFont().family(),
            "size": self.size_spin.value(),
            "bold": self.bold_check.isChecked(),
            "italic": self.italic_check.isChecked(),
            "underline": self.underline_check.isChecked(),
        }

    def apply_and_close(self):
        try:
            config = self.get_config()
            FontManager.save_config(config)
            parent = self.parent()
            if parent:
                self._refresh_all_result_widgets(parent)
                if hasattr(parent, 'leitor') and hasattr(parent.leitor, 'atualizar_fonte_persistente'):
                    try:
                        parent.leitor.atualizar_fonte_persistente()

                    except Exception as e:
                        logger.error(f"Erro ao sincronizar leitor: {e}", exc_info=True)

            self.accept()

        except Exception as e:
            logger.error(f"Erro ao aplicar configuração: {e}", exc_info=True)

    def _refresh_all_result_widgets(self, parent):
        try:
            from PySide6.QtWidgets import QWidget, QTextEdit, QPlainTextEdit
            from PySide6.QtGui import QTextCursor, QTextCharFormat

            config = FontManager.get_config()
            font = QFont(config["family"], config["size"])
            font.setBold(config.get("bold", False))
            font.setItalic(config.get("italic", False))
            font.setUnderline(config.get("underline", False))

            if not isinstance(parent, QWidget):
                return

            BLACKLIST = {"feynman_user_input"}

            for w in parent.findChildren(QWidget):
                try:
                    if isinstance(w, (QTextEdit, QPlainTextEdit)):
                        if w.objectName() in BLACKLIST:
                            continue

                        try:
                            doc = w.document()
                            try:
                                doc.setDefaultFont(font)

                            except Exception as e:
                                logger.error(f"Erro ao definir fonte padrão do documento: {e}", exc_info=True)

                            try:
                                if not doc.isEmpty():
                                    cursor = QTextCursor(doc)
                                    cursor.select(QTextCursor.Document)
                                    fmt = QTextCharFormat()
                                    fmt.setFont(font)
                                    cursor.mergeCharFormat(fmt)

                            except Exception as e:
                                logger.error(f"Erro ao atualizar formato do documento: {e}", exc_info=True)

                        except Exception as e:
                            logger.error(f"Erro ao definir fonte padrão do documento: {e}", exc_info=True)

                    if hasattr(w, 'refresh_all_fonts'):
                        try:
                            w.refresh_all_fonts(font)

                        except TypeError:
                            try:
                                w.refresh_all_fonts()

                            except Exception as e:
                                logger.error(f"Erro ao atualizar fonte no widget {type(w)}: {e}", exc_info=True)

                except Exception as e_widget:
                    logger.error(f"Erro ao atualizar fonte no widget {type(w)}: {e_widget}", exc_info=True)

        except Exception as e:
            logger.error(f"Erro ao atualizar fontes filtradas: {e}", exc_info=True)

    def reset_to_default(self):
        try:
            FontManager.reset_to_default()
            self.load_config()

        except Exception as e:
            logger.error(f"Erro ao resetar configuração: {e}", exc_info=True)
