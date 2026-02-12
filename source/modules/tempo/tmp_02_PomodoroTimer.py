from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QGroupBox, QProgressBar, QMessageBox
from PySide6.QtCore import Qt, QTimer, Signal, QCoreApplication, QEvent
from PySide6.QtGui import QFont, QIcon
from source.utils.LogManager import LogManager
from source.utils.GerenciadorBotoesUI import GerenciadorBotoesUI
from source.utils.IconUtils import get_icon_path
from source.utils.SoundManager import SoundManager


class PomodoroTimer(QWidget):
    ciclo_completado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LogManager.get_logger()
        try:
            self.tempo_foco = 25 * 60
            self.tempo_descanso_curto = 5 * 60
            self.tempo_descanso_longo = 15 * 60
            self.tempo_restante = self.tempo_foco
            self.em_foco = True
            self.ciclos_completados = 0
            self.timer_ativo = False
            self.gerenciador_botoes = GerenciadorBotoesUI(self)

            self._sound_mgr = SoundManager.instance()

            self.timer = QTimer()
            self.timer.timeout.connect(self.atualizar_timer)

            self.setup_ui()

            app = QCoreApplication.instance()
            if app:
                app.installEventFilter(self)

            self._aplicar_tema_dinamico()

        except Exception as e:
            self.logger.error(f"Erro ao inicializar PomodoroTimer: {str(e)}", exc_info=True)

    def setup_ui(self):
        try:
            layout = QVBoxLayout()

            self.label_tempo = QLabel("25:00")
            fonte = QFont("Arial", 48, QFont.Bold)
            self.label_tempo.setFont(fonte)
            self.label_tempo.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.label_tempo)

            self.progress = QProgressBar()
            self.progress.setMaximum(self.tempo_foco)
            self.progress.setValue(self.tempo_foco)
            self.progress.setTextVisible(False)
            layout.addWidget(self.progress)

            self.label_status = QLabel()
            self.label_status.setAlignment(Qt.AlignCenter)
            self.label_status.setStyleSheet("font-size: 14pt; font-weight: bold;")
            layout.addWidget(self.label_status)

            controles = QHBoxLayout()

            self.btn_iniciar = self.gerenciador_botoes.create_button()
            self.btn_iniciar.setIcon(QIcon(get_icon_path("play")))
            self.btn_iniciar.clicked.connect(self.toggle_timer)
            controles.addWidget(self.btn_iniciar)

            self.btn_resetar = self.gerenciador_botoes.create_button()
            self.btn_resetar.setIcon(QIcon(get_icon_path("reset")))
            self.btn_resetar.clicked.connect(self.resetar_timer)
            controles.addWidget(self.btn_resetar)

            self.btn_resetar_ciclo = self.gerenciador_botoes.create_button()
            self.btn_resetar_ciclo.setIcon(QIcon(get_icon_path("reset")))
            self.btn_resetar_ciclo.clicked.connect(self.resetar_ciclo)
            controles.addWidget(self.btn_resetar_ciclo)

            self.btn_pular = self.gerenciador_botoes.create_button()
            self.btn_pular.setIcon(QIcon(get_icon_path("skip")))
            self.btn_pular.clicked.connect(self.pular_ciclo)
            controles.addWidget(self.btn_pular)

            layout.addLayout(controles)

            self.config_group = QGroupBox()
            config_layout = QHBoxLayout()

            self.label_foco = QLabel()
            config_layout.addWidget(self.label_foco)

            self.spin_foco = QComboBox()
            self.spin_foco.addItems(["1", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"])
            self.spin_foco.setCurrentText("25")
            self.spin_foco.currentTextChanged.connect(self.atualizar_configuracoes)
            config_layout.addWidget(self.spin_foco)

            self.label_descanso = QLabel()
            config_layout.addWidget(self.label_descanso)

            self.spin_descanso = QComboBox()
            self.spin_descanso.addItems(["1", "3", "5", "7", "10", "15", "20", "25", "30"])
            self.spin_descanso.setCurrentText("5")
            self.spin_descanso.currentTextChanged.connect(self.atualizar_configuracoes)
            config_layout.addWidget(self.spin_descanso)

            self.config_group.setLayout(config_layout)
            layout.addWidget(self.config_group)

            self.setLayout(layout)
            self.atualizar_traducoes()

        except Exception as e:
            self.logger.error(f"Erro ao configurar interface do PomodoroTimer: {str(e)}", exc_info=True)

    def atualizar_traducoes(self):
        try:
            ciclo_atual = (self.ciclos_completados % 4) + 1

            if self.em_foco:
                self.label_status.setText(QCoreApplication.translate("App", "🎯 Modo: Foco | Ciclo: {ciclo}/4").format(ciclo=ciclo_atual))

            else:
                tipo_descanso = QCoreApplication.translate("App", "Longo") if self.ciclos_completados % 4 == 0 else QCoreApplication.translate("App", "Curto")
                self.label_status.setText(QCoreApplication.translate("App", "☕ Modo: Descanso {tipo} | Ciclo: {ciclo}/4").format(tipo=tipo_descanso, ciclo=ciclo_atual))

            texto_iniciar = (QCoreApplication.translate("App", "⏸️ Pausar") if self.timer_ativo else QCoreApplication.translate("App", "▶️ Iniciar"))

            self.gerenciador_botoes.set_button_text(self.btn_iniciar, texto_iniciar)

            self.gerenciador_botoes.set_button_text(self.btn_resetar, QCoreApplication.translate("App", "⏱️ Resetar Relógio"))
            self.gerenciador_botoes.set_button_text(self.btn_pular, QCoreApplication.translate("App", "⏭️ Pular"))

            if hasattr(self, 'btn_resetar_ciclo'):
                self.gerenciador_botoes.set_button_text(self.btn_resetar_ciclo, QCoreApplication.translate("App", "🔄 Resetar Ciclo"))

            self.config_group.setTitle(QCoreApplication.translate("App", "⚙️ Configurações"))
            self.label_foco.setText(QCoreApplication.translate("App", "Foco (min):"))
            self.label_descanso.setText(QCoreApplication.translate("App", "Descanso (min):"))

            self._aplicar_tema_dinamico()

        except Exception as e:
            self.logger.error(f"Erro ao atualizar traduções do PomodoroTimer: {str(e)}", exc_info=True)

    def atualizar_configuracoes(self):
        try:
            novo_foco = int(self.spin_foco.currentText()) * 60
            novo_descanso_curto = int(self.spin_descanso.currentText()) * 60

            if self.em_foco:
                total_antigo = self.tempo_foco

            else:
                total_antigo = self.tempo_descanso_longo if (self.ciclos_completados % 4 == 0) else self.tempo_descanso_curto

            decorrido = max(0, total_antigo - self.tempo_restante)

            self.tempo_foco = novo_foco
            self.tempo_descanso_curto = novo_descanso_curto

            if self.em_foco:
                total_novo = self.tempo_foco

            else:
                total_novo = self.tempo_descanso_longo if (self.ciclos_completados % 4 == 0) else self.tempo_descanso_curto

            self.tempo_restante = max(total_novo - decorrido, 0)

            self.progress.setMaximum(total_novo)
            self.progress.setValue(self.tempo_restante)
            self.atualizar_display()
            self.atualizar_traducoes()

        except Exception as e:
            self.logger.error(f"Erro ao atualizar configurações do timer: {str(e)}", exc_info=True)

    def toggle_timer(self):
        try:
            if self.timer_ativo:
                self.timer.stop()
                self.timer_ativo = False
                self.gerenciador_botoes.set_button_text(self.btn_iniciar, QCoreApplication.translate("App", "▶️ Continuar"))

            else:
                self.timer.start(1000)
                self.timer_ativo = True
                self.gerenciador_botoes.set_button_text(self.btn_iniciar, QCoreApplication.translate("App", "⏸️ Pausar"))

        except Exception as e:
            self.logger.error(f"Erro ao alternar estado do timer: {str(e)}", exc_info=True)

    def atualizar_timer(self):
        try:
            self.tempo_restante -= 1
            self.progress.setValue(self.tempo_restante)
            self.atualizar_display()

            if self.tempo_restante <= 0:
                self.timer.stop()
                self.finalizar_ciclo()

        except Exception as e:
            self.logger.error(f"Erro ao atualizar timer: {str(e)}", exc_info=True)

    def atualizar_display(self):
        try:
            minutos = self.tempo_restante // 60
            segundos = self.tempo_restante % 60
            self.label_tempo.setText(f"{minutos:02d}:{segundos:02d}")

        except Exception as e:
            self.logger.error(f"Erro ao atualizar display do timer: {str(e)}", exc_info=True)

    def _executar_alerta(self, titulo, texto):
        try:
            self._sound_mgr.play_looping()

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(titulo)
            msg.setText(texto)
            msg.finished.connect(lambda _: self._sound_mgr.stop())
            msg.exec()

        except Exception as e:
            self.logger.error(f"Erro ao executar alerta com som: {e}", exc_info=True)
            QMessageBox.information(self, titulo, texto)
            try:
                self._sound_mgr.stop()

            except Exception as e:
                self.logger.error(f"Erro ao parar som do alerta: {e}", exc_info=True)

    def finalizar_ciclo(self):
        try:
            if self.em_foco:
                self.ciclos_completados += 1
                self.ciclo_completado.emit("foco")

                self._executar_alerta(
                    QCoreApplication.translate("App", "🎉 Ciclo Completo!"),
                    QCoreApplication.translate("App",
                        "Parabéns! Você completou um ciclo de foco.\n"
                        "Ciclos hoje: {ciclos}\n\n"
                        "Hora de descansar! 😊"
                    ).format(ciclos=self.ciclos_completados)
                )

                if self.ciclos_completados % 4 == 0:
                    self.tempo_restante = self.tempo_descanso_longo
                    tipo_descanso = QCoreApplication.translate("App", "Longo")

                else:
                    self.tempo_restante = self.tempo_descanso_curto
                    tipo_descanso = QCoreApplication.translate("App", "Curto")

                self.em_foco = False
                ciclo_atual = (self.ciclos_completados % 4) + 1
                self.label_status.setText(QCoreApplication.translate("App", "☕ Modo: Descanso {tipo} | Ciclo: {ciclo}/4").format(tipo=tipo_descanso, ciclo=ciclo_atual))
                self.progress.setMaximum(self.tempo_restante)
                self.progress.setValue(self.tempo_restante)

            else:
                self.ciclo_completado.emit("descanso")

                self._executar_alerta(
                    QCoreApplication.translate("App", "✅ Descanso Completo"),
                    QCoreApplication.translate("App",
                        "Descanso finalizado!\n"
                        "Vamos para o próximo ciclo de foco! 💪"
                    )
                )

                self.em_foco = True
                self.tempo_restante = self.tempo_foco
                ciclo_atual = (self.ciclos_completados % 4) + 1
                self.label_status.setText(QCoreApplication.translate("App", "🎯 Modo: Foco | Ciclo: {ciclo}/4").format(ciclo=ciclo_atual))
                self.progress.setMaximum(self.tempo_foco)
                self.progress.setValue(self.tempo_foco)

            self.atualizar_display()
            self.timer_ativo = False
            self.gerenciador_botoes.set_button_text(self.btn_iniciar, QCoreApplication.translate("App", "▶️ Iniciar"))

        except Exception as e:
            self.logger.error(f"Erro ao finalizar ciclo: {str(e)}", exc_info=True)

    def resetar_timer(self):
        try:
            self.timer.stop()
            self.timer_ativo = False
            self.tempo_restante = self.tempo_foco if self.em_foco else (self.tempo_descanso_longo if (self.ciclos_completados % 4 == 0) else self.tempo_descanso_curto)
            self.progress.setMaximum(self.tempo_restante)
            self.progress.setValue(self.tempo_restante)
            self.atualizar_display()
            self.gerenciador_botoes.set_button_text(self.btn_iniciar, QCoreApplication.translate("App", "▶️ Iniciar"))

        except Exception as e:
            self.logger.error(f"Erro ao resetar timer: {str(e)}", exc_info=True)

    def resetar_ciclo(self):
        try:
            self.timer.stop()
            self.timer_ativo = False
            self.em_foco = True
            self.ciclos_completados = 0
            self.tempo_restante = self.tempo_foco
            self.progress.setMaximum(self.tempo_foco)
            self.progress.setValue(self.tempo_foco)
            self.atualizar_display()

            self.gerenciador_botoes.set_button_text(self.btn_iniciar, QCoreApplication.translate("App", "▶️ Iniciar"))
            self.atualizar_traducoes()

        except Exception as e:
            self.logger.error(f"Erro ao resetar ciclo: {str(e)}", exc_info=True)

    def pular_ciclo(self):
        try:
            self.timer.stop()
            self.tempo_restante = 0
            self.finalizar_ciclo()

        except Exception as e:
            self.logger.error(f"Erro ao pular ciclo: {str(e)}", exc_info=True)

    def _aplicar_tema_dinamico(self):
        try:
            app = QCoreApplication.instance()
            if not app:
                return

            pal = app.palette()

            for lbl in (self.label_status, self.label_tempo):
                lbl.setPalette(pal)
                lbl.setAutoFillBackground(False)

            self.update()

        except Exception as e:
            self.logger.error(f"Erro ao aplicar tema dinâmico PomodoroTimer: {str(e)}", exc_info=True)

    def eventFilter(self, obj, event):
        try:
            tipos = (
                QEvent.ApplicationPaletteChange,
                QEvent.PaletteChange,
                QEvent.StyleChange,
            )

            try:
                tipos = tipos + (QEvent.ColorSchemeChange,)

            except AttributeError:
                pass

            if event.type() in tipos:
                self._aplicar_tema_dinamico()

        except Exception as e:
            self.logger.error(f"Erro no eventFilter PomodoroTimer: {str(e)}", exc_info=True)

        return super().eventFilter(obj, event)
