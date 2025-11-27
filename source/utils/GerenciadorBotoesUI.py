from source.utils.LogManager import LogManager
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer
from source.utils.IconUtils import get_icon_path
logger = LogManager.get_logger()


class GerenciadorBotoesUI:
    def __init__(self, parent):
        self.parent = parent
        self.buttons_data = []
        self.managed_buttons = []

    def add_button_with_label(self, layout, label_text, icon_name, callback, icon_path=None, translation_key=None):
        try:
            layout_h = QHBoxLayout()
            label = QLabel(label_text, self.parent)
            layout_h.addWidget(label)

            button = self.create_button()
            icon_file = get_icon_path(icon_name)
            button.setIcon(QIcon(icon_file))
            button.clicked.connect(callback)
            layout_h.addWidget(button)
            layout.addLayout(layout_h)

            if translation_key is None:
                translation_key = label_text

            self.buttons_data.append({'label': label, 'translation_key': translation_key})
            return button

        except Exception as e:
            logger.error(f"Erro ao adicionar botão: {e}", exc_info=True)

    def update_buttons_text(self, loc):
        try:
            for entry in self.buttons_data:
                entry['label'].setText(loc.get_text(entry['translation_key']))

        except Exception as e:
            logger.error(f"Erro ao atualizar texto dos botões: {e}", exc_info=True)

    def create_button(self, text="", min_padding=20):
        try:
            button = QPushButton(text)
            button.setFont(QFont('Arial', 9))

            self.managed_buttons.append({
                'button': button,
                'min_padding': min_padding
            })

            button.textChanged = lambda: self._resize_button(button, min_padding)

            if text:
                self._resize_button(button, min_padding)

            else:
                button.setMinimumWidth(3 * button.fontMetrics().horizontalAdvance('m'))
                button.setMaximumWidth(3 * button.fontMetrics().horizontalAdvance('m'))

            return button

        except Exception as e:
            logger.error(f"Erro ao criar botão: {e}", exc_info=True)
            return QPushButton()

    def _resize_button(self, button, min_padding=20):
        try:
            text = button.text()
            if not text:
                button.setMinimumWidth(3 * button.fontMetrics().horizontalAdvance('m'))
                button.setMaximumWidth(3 * button.fontMetrics().horizontalAdvance('m'))
                return

            font_metrics = button.fontMetrics()
            text_width = font_metrics.horizontalAdvance(text)

            icon_width = 0
            if not button.icon().isNull():
                icon_size = button.iconSize()
                icon_width = icon_size.width() + 4

            total_width = text_width + icon_width + min_padding

            button.setMinimumWidth(total_width)
            button.setMaximumWidth(total_width)

            logger.debug(f"Botão '{text}' redimensionado para {total_width}px")

        except Exception as e:
            logger.error(f"Erro ao redimensionar botão: {e}", exc_info=True)

    def update_all_button_sizes(self):
        try:
            for button_data in self.managed_buttons:
                button = button_data['button']
                min_padding = button_data['min_padding']
                self._resize_button(button, min_padding)

            logger.debug(f"Tamanhos atualizados para {len(self.managed_buttons)} botões")

        except Exception as e:
            logger.error(f"Erro ao atualizar tamanhos dos botões: {e}", exc_info=True)

    def set_button_text(self, button, text):
        try:
            button.setText(text)

            min_padding = 20
            for button_data in self.managed_buttons:
                if button_data['button'] == button:
                    min_padding = button_data['min_padding']
                    break

            QTimer.singleShot(0, lambda: self._resize_button(button, min_padding))

        except Exception as e:
            logger.error(f"Erro ao definir texto do botão: {e}", exc_info=True)

    def create_button_with_auto_resize(self, text="", icon_name=None, min_padding=20):
        try:
            button = self.create_button(text, min_padding)

            if icon_name:
                icon_file = get_icon_path(icon_name)
                button.setIcon(QIcon(icon_file))

            return button

        except Exception as e:
            logger.error(f"Erro ao criar botão com auto-resize: {e}", exc_info=True)
            return QPushButton()
