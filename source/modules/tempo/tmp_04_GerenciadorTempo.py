from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QGroupBox
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtGui import QPalette
from source.utils.LogManager import LogManager
from source.modules.tempo.tmp_01_Tarefa import Tarefa
from source.modules.tempo.tmp_02_PomodoroTimer import PomodoroTimer
from source.modules.tempo.tmp_03_GerenciadorTarefas import GerenciadorTarefas


class GerenciadorTempo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LogManager.get_logger()
        try:
            self.setup_ui()

            app = QCoreApplication.instance()
            if app:
                app.installEventFilter(self)

            self._aplicar_tema_dinamico_inputs()

        except Exception as e:
            self.logger.error(f"Erro ao inicializar GerenciadorTempo: {str(e)}", exc_info=True)

    def setup_ui(self):
        try:
            layout = QVBoxLayout()

            topo = QHBoxLayout()

            self.pomodoro = PomodoroTimer(self)
            self.pomodoro.ciclo_completado.connect(self.registrar_pomodoro)
            topo.addWidget(self.pomodoro, 2)

            self.col_doing_timer_group = QGroupBox()
            doing_timer_layout = QVBoxLayout()
            self.col_doing_timer_list = QListWidget()
            self.col_doing_timer_list.setDragDropMode(QListWidget.NoDragDrop)
            doing_timer_layout.addWidget(self.col_doing_timer_list)
            self.col_doing_timer_group.setLayout(doing_timer_layout)
            topo.addWidget(self.col_doing_timer_group, 1)

            layout.addLayout(topo)

            self.label_tarefas = QLabel()
            self.label_tarefas.setStyleSheet("font-size: 16pt; font-weight: bold; margin-top: 20px;")
            layout.addWidget(self.label_tarefas)

            self.tarefas = GerenciadorTarefas(self)
            self.tarefas.listas_atualizadas.connect(self.atualizar_coluna_doing_timer)
            layout.addWidget(self.tarefas)

            self.setLayout(layout)
            self.atualizar_traducoes()

            self.atualizar_coluna_doing_timer()

        except Exception as e:
            self.logger.error(f"Erro ao configurar interface do GerenciadorTempo: {str(e)}", exc_info=True)

    def _aplicar_tema_dinamico_inputs(self):
        try:
            app = QCoreApplication.instance()
            if not app:
                return

            window_color = app.palette().color(QPalette.Window)

            pal = self.col_doing_timer_list.palette()
            pal.setColor(QPalette.Base, window_color)
            pal.setColor(QPalette.AlternateBase, window_color)
            self.col_doing_timer_list.setPalette(pal)
            self.col_doing_timer_list.viewport().setAutoFillBackground(True)

            self.update()

        except Exception as e:
            self.logger.error(f"Erro ao aplicar tema dinâmico (lista) no GerenciadorTempo: {str(e)}", exc_info=True)

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
                self._aplicar_tema_dinamico_inputs()

        except Exception as e:
            self.logger.error(f"Erro no eventFilter do GerenciadorTempo: {str(e)}", exc_info=True)

        return super().eventFilter(obj, event)

    def atualizar_traducoes(self):
        try:
            self.label_tarefas.setText(QCoreApplication.translate("App", "📊 Quadro de Tarefas"))

            if hasattr(self, 'pomodoro') and self.pomodoro:
                self.pomodoro.atualizar_traducoes()

            if hasattr(self, 'tarefas') and self.tarefas:
                self.tarefas.atualizar_traducoes()

            if hasattr(self, 'col_doing_timer_group') and self.col_doing_timer_group:
                self.col_doing_timer_group.setTitle(QCoreApplication.translate("App", "⚙️ Em Progresso"))

        except Exception as e:
            self.logger.error(f"Erro ao atualizar traduções do GerenciadorTempo: {str(e)}", exc_info=True)

    def registrar_pomodoro(self, tipo):
        try:
            if tipo != "foco":
                return

            if not hasattr(self, 'tarefas') or not self.tarefas:
                return

            alterou = False
            for t in getattr(self.tarefas, 'tarefas', []):
                if getattr(t, 'status', '') == "Doing":
                    t.pomodoros_completados = int(getattr(t, 'pomodoros_completados', 0)) + 1
                    alterou = True

            if alterou:
                self.tarefas.salvar_tarefas()
                self.tarefas.atualizar_listas()
                self.atualizar_coluna_doing_timer()

        except Exception as e:
            self.logger.error(f"Erro ao registrar pomodoro nas tarefas em progresso: {str(e)}", exc_info=True)

    def atualizar_coluna_doing_timer(self):
        try:
            self.col_doing_timer_list.clear()

            if not hasattr(self, 'tarefas') or not self.tarefas:
                return

            for t in getattr(self.tarefas, 'tarefas', []):
                if getattr(t, 'status', '') == "Doing":
                    prioridade_norm = Tarefa.normalizar_prioridade(getattr(t, 'prioridade', 'Média'))
                    emoji = {"Alta": "🔴", "Média": "🟡", "Baixa": "🟢"}.get(prioridade_norm, "🟡")
                    texto = f"{emoji} {t.titulo} — 🍅 {t.pomodoros_completados}"
                    self.col_doing_timer_list.addItem(texto)

        except Exception as e:
            self.logger.error(f"Erro ao atualizar coluna de tarefas em progresso no timer: {str(e)}", exc_info=True)
