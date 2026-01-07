from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                               QPushButton, QSpinBox, QGroupBox, QFormLayout)
from PySide6.QtCore import QCoreApplication
from source.utils.SoundManager import SoundManager
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()


class SoundConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setWindowTitle(QCoreApplication.translate("App", "🔔 Configurar Som do Pomodoro"))
            self.setMinimumWidth(450)
            self._mgr = SoundManager.instance()
            layout = QVBoxLayout()

            sound_group = QGroupBox(QCoreApplication.translate("App", "🔊 Campainha"))
            sound_layout = QVBoxLayout()
            sound_layout.addWidget(QLabel(QCoreApplication.translate("App", "Selecione a campainha para tocar ao final do Pomodoro / Pausa:")))

            self.combo = QComboBox()
            self._paths = self._mgr.get_available_sounds()
            for p in self._paths:
                self.combo.addItem(self._mgr.get_sound_display_name(p), p)

            cur = self._mgr.get_current_sound()
            if cur in self._paths:
                idx = self._paths.index(cur)
                self.combo.setCurrentIndex(idx)

            self.combo.currentIndexChanged.connect(self._on_sound_changed)
            sound_layout.addWidget(self.combo)

            self.label_duration = QLabel()
            self.label_duration.setStyleSheet("color: #666; font-size: 9pt;")
            self._update_duration_label()
            sound_layout.addWidget(self.label_duration)

            preview_layout = QHBoxLayout()

            self.btn_play = QPushButton(QCoreApplication.translate("App", "▶️ Tocar"))
            self.btn_play.clicked.connect(self.on_play)
            preview_layout.addWidget(self.btn_play)

            self.btn_stop_preview = QPushButton(QCoreApplication.translate("App", "⏹️ Parar"))
            self.btn_stop_preview.clicked.connect(self.on_stop_preview)
            preview_layout.addWidget(self.btn_stop_preview)

            sound_layout.addLayout(preview_layout)

            sound_group.setLayout(sound_layout)
            layout.addWidget(sound_group)

            interval_group = QGroupBox(QCoreApplication.translate("App", "⏱️ Repetição do Alarme"))
            interval_layout = QFormLayout()

            self.spin_interval = QSpinBox()
            self.spin_interval.setMinimum(0)
            self.spin_interval.setMaximum(60)
            self.spin_interval.setValue(self._mgr.get_alarm_interval())
            self.spin_interval.setSuffix(QCoreApplication.translate("App", " segundos"))
            self.spin_interval.valueChanged.connect(self._update_total_label)

            interval_layout.addRow(QLabel(QCoreApplication.translate("App", "Intervalo entre repetições:")), self.spin_interval)

            self.label_total = QLabel()
            self.label_total.setStyleSheet("color: #007ACC; font-size: 9pt; font-weight: bold;")
            self._update_total_label()
            interval_layout.addRow(self.label_total)

            hint_label = QLabel(QCoreApplication.translate("App", 
                "💡 O alarme tocará por completo e, após o intervalo definido,\n"
                "repetirá até você fechar a janela de alerta.\n"
                "Defina 0 para repetir imediatamente após o áudio terminar."))
            hint_label.setWordWrap(True)
            hint_label.setStyleSheet("color: gray; font-size: 9pt;")
            interval_layout.addRow(hint_label)

            interval_group.setLayout(interval_layout)
            layout.addWidget(interval_group)

            h = QHBoxLayout()
            self.btn_save = QPushButton(QCoreApplication.translate("App", "💾 Salvar"))
            self.btn_cancel = QPushButton(QCoreApplication.translate("App", "Cancelar"))

            self.btn_save.clicked.connect(self.on_save)
            self.btn_cancel.clicked.connect(self.reject)

            h.addStretch()
            h.addWidget(self.btn_save)
            h.addWidget(self.btn_cancel)
            layout.addLayout(h)

            self.setLayout(layout)

        except Exception as e:
            logger.error(f"Error initializing SoundConfigDialog: {e}")

    def _on_sound_changed(self, index):
        self.on_stop_preview()
        self._update_duration_label()
        self._update_total_label()

    def _update_duration_label(self):
        path = self.combo.currentData()
        if path:
            duration_ms = self._mgr.get_duration_for_path(path)
            duration_s = duration_ms / 1000
            duration_formatted = f"{duration_s:.2f}"
            self.label_duration.setText(QCoreApplication.translate("App", "⏱️ Duração do áudio: {duration} segundos").format(duration=duration_formatted))

    def _update_total_label(self):
        path = self.combo.currentData()
        if path:
            duration_ms = self._mgr.get_duration_for_path(path)
            interval_s = self.spin_interval.value()
            total_s = (duration_ms / 1000) + interval_s
            total_formatted = f"{total_s:.2f}"
            self.label_total.setText(QCoreApplication.translate("App", "🔄 Repetição a cada: {total} segundos").format(total=total_formatted))

    def on_play(self):
        try:
            path = self.combo.currentData()
            if path:
                self._mgr.preview(path)
                logger.debug(f"Preview iniciado: {path}")

        except Exception as e:
            logger.error(f"Error playing sound preview: {e}")

    def on_stop_preview(self):
        try:
            self._mgr.stop()
            logger.debug("Preview parado pelo usuário")

        except Exception as e:
            logger.error(f"Error stopping sound preview: {e}")

    def on_save(self):
        try:
            self.on_stop_preview()

            path = self.combo.currentData()
            if path:
                self._mgr.set_sound(path)

            interval = self.spin_interval.value()
            self._mgr.set_alarm_interval(interval)

        except Exception as e:
            logger.error(f"Error saving sound configuration: {e}")

        self.accept()

    def closeEvent(self, event):
        try:
            self.on_stop_preview()

        except Exception as e:
            logger.error(f"Error stopping preview on dialog close: {e}")

        super().closeEvent(event)
