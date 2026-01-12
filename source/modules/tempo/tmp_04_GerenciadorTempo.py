from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QGroupBox, QPushButton
from PySide6.QtCore import QCoreApplication, QEvent, QThread, QObject, Signal, Slot
from PySide6.QtGui import QPalette
from source.utils.LogManager import LogManager
from source.modules.tempo.tmp_01_Tarefa import Tarefa
from source.modules.tempo.tmp_02_PomodoroTimer import PomodoroTimer
from source.modules.tempo.tmp_03_GerenciadorTarefas import GerenciadorTarefas
from source.utils.EventBus import get_event_bus
from uuid import uuid4


class _TimeWorker(QObject):
    pomodoro_completed = Signal(str)

    def __init__(self):
        super().__init__()
        self.logger = LogManager.get_logger()
        self._running = True

    @Slot(str)
    def on_pomodoro(self, tipo: str):
        try:
            self.logger.debug(f"Worker de tempo recebeu evento de pomodoro: {tipo}")
            self.pomodoro_completed.emit(tipo)

        except Exception as e:
            try:
                self.logger.error(f"Erro no TimeWorker.on_pomodoro: {e}", exc_info=True)

            except Exception:
                pass

    @Slot()
    def stop(self):
        try:
            self._running = False

        except Exception:
            pass


class GerenciadorTempo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LogManager.get_logger()
        try:
            self._integracao_ids_recebidos = set()
            self._tempo_thread = QThread()
            self._tempo_worker = _TimeWorker()
            self._tempo_worker.moveToThread(self._tempo_thread)
            self._tempo_worker.pomodoro_completed.connect(self.registrar_pomodoro)
            self._tempo_thread.start()

            self.setup_ui()
            self._setup_integracao_eisenhower()

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
            self.pomodoro.ciclo_completado.connect(self._tempo_worker.on_pomodoro)
            topo.addWidget(self.pomodoro, 2)

            self.col_doing_timer_group = QGroupBox()
            doing_timer_layout = QVBoxLayout()
            self.col_doing_timer_list = QListWidget()
            self.col_doing_timer_list.setDragDropMode(QListWidget.NoDragDrop)
            doing_timer_layout.addWidget(self.col_doing_timer_list)
            self.col_doing_timer_group.setLayout(doing_timer_layout)
            topo.addWidget(self.col_doing_timer_group, 1)

            layout.addLayout(topo)

            header = QHBoxLayout()
            self.label_tarefas = QLabel()
            self.label_tarefas.setStyleSheet("font-size: 16pt; font-weight: bold; margin-top: 20px;")
            header.addWidget(self.label_tarefas, 1)

            self.btn_eisenhower_integrado = QPushButton()
            self.btn_eisenhower_integrado.setCheckable(True)
            self.btn_eisenhower_integrado.setChecked(False)

            try:
                self.btn_eisenhower_integrado.toggled.connect(lambda _: self._atualizar_rotulo_botao_eisenhower())

            except Exception:
                pass

            header.addWidget(self.btn_eisenhower_integrado, 0)
            layout.addLayout(header)

            self.tarefas = GerenciadorTarefas(self)
            self.tarefas.listas_atualizadas.connect(self.atualizar_coluna_doing_timer)

            try:
                self.tarefas.tarefa_adicionada.connect(self._on_tarefa_adicionada_gestao_tempo)

            except Exception:
                pass

            layout.addWidget(self.tarefas)

            self.setLayout(layout)
            self.atualizar_traducoes()
            self.atualizar_coluna_doing_timer()

        except Exception as e:
            self.logger.error(f"Erro ao configurar interface do GerenciadorTempo: {str(e)}", exc_info=True)

    def _atualizar_rotulo_botao_eisenhower(self) -> None:
        try:
            if not hasattr(self, 'btn_eisenhower_integrado') or not self.btn_eisenhower_integrado:
                return

            if self.btn_eisenhower_integrado.isChecked():
                self.btn_eisenhower_integrado.setText(QCoreApplication.translate("App", "🗂️ Matriz Eisenhower Conectada"))

            else:
                self.btn_eisenhower_integrado.setText(QCoreApplication.translate("App", "🗂️ Matriz Eisenhower Desconectada"))

        except Exception:
            pass

    def _setup_integracao_eisenhower(self):
        try:
            self._event_bus = get_event_bus()
            try:
                self._event_bus.tarefa_integracao.connect(self._on_event_bus_tarefa)

            except Exception:
                pass

            try:
                self._event_bus.drain_pending_tarefas()

            except Exception:
                pass

        except Exception as e:
            self.logger.debug(f"Falha ao configurar integração com Eisenhower: {e}", exc_info=True)

    def _on_tarefa_adicionada_gestao_tempo(self, dados: dict):
        try:
            if not hasattr(self, 'btn_eisenhower_integrado') or not self.btn_eisenhower_integrado.isChecked():
                return

            titulo = (dados or {}).get("titulo")
            prioridade = (dados or {}).get("prioridade")
            if not titulo:
                return

            payload = {
                "integration_id": str(uuid4()),
                "origin": "tempo",
                "titulo": titulo,
                "prioridade": Tarefa.normalizar_prioridade(prioridade),
            }
            get_event_bus().send_tarefa(payload)

        except Exception as e:
            self.logger.debug(f"Falha ao enviar tarefa para Eisenhower: {e}", exc_info=True)

    def _on_event_bus_tarefa(self, dados: dict):
        try:
            payload = dados or {}
            if payload.get("origin") != "eisenhower":
                return

            integration_id = payload.get("integration_id")
            if integration_id and integration_id in self._integracao_ids_recebidos:
                return

            if integration_id:
                self._integracao_ids_recebidos.add(integration_id)

            titulo = (payload.get("titulo") or "").strip()
            prioridade = payload.get("prioridade") or "Importante e Urgente"

            if not titulo:
                return

            if hasattr(self, 'tarefas') and self.tarefas:
                self.tarefas.adicionar_tarefa_externa(titulo=titulo, prioridade=prioridade)

        except Exception as e:
            self.logger.debug(f"Falha ao receber tarefa do Eisenhower: {e}", exc_info=True)

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

            if hasattr(self, 'btn_eisenhower_integrado') and self.btn_eisenhower_integrado:
                self._atualizar_rotulo_botao_eisenhower()
                self.btn_eisenhower_integrado.setToolTip(
                    QCoreApplication.translate("App", "Quando ativado, tarefas adicionadas aqui também são enviadas para a Matriz de Eisenhower.")
                )

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

    def cleanup(self):
        try:
            try:
                if hasattr(self, 'pomodoro') and self.pomodoro and hasattr(self, '_tempo_worker'):
                    try:
                        self.pomodoro.ciclo_completado.disconnect(self._tempo_worker.on_pomodoro)

                    except Exception:
                        pass

            except Exception:
                pass

            try:
                if hasattr(self, '_tempo_worker') and self._tempo_worker is not None:
                    try:
                        self._tempo_worker.stop()

                    except Exception:
                        pass

            except Exception:
                pass

            if hasattr(self, '_tempo_thread'):
                try:
                    try:
                        running = False
                        try:
                            running = self._tempo_thread.isRunning()

                        except RuntimeError:
                            running = False

                        except Exception:
                            running = False

                        if running:
                            try:
                                self._tempo_thread.quit()
                                self._tempo_thread.wait(2000)

                            except RuntimeError:
                                pass

                            except Exception:
                                try:
                                    self._tempo_thread.terminate()

                                except Exception:
                                    pass

                    except RuntimeError:
                        pass

                except Exception:
                    pass

            try:
                if hasattr(self, '_tempo_worker'):
                    self._tempo_worker = None

            except Exception:
                pass

            try:
                if hasattr(self, '_tempo_thread'):
                    self._tempo_thread = None

            except Exception:
                pass

        except Exception as e:
            self.logger.error(f"Erro ao limpar GerenciadorTempo: {e}", exc_info=True)

    def __del__(self):
        try:
            self.cleanup()

        except Exception:
            pass

    def atualizar_coluna_doing_timer(self):
        try:
            self.col_doing_timer_list.clear()

            if not hasattr(self, 'tarefas') or not self.tarefas:
                return

            for t in getattr(self.tarefas, 'tarefas', []):
                if getattr(t, 'status', '') == "Doing":
                    prioridade_norm = Tarefa.normalizar_prioridade(getattr(t, 'prioridade', 'Importante e Urgente'))
                    emoji = {
                        "Importante e Urgente": "🔴",
                        "Importante, mas Não Urgente": "🟠",
                        "Não Importante, mas Urgente": "🟡",
                        "Não Importante e Não Urgente": "🟢",
                    }.get(prioridade_norm, "🔴")
                    texto = f"{emoji} {t.titulo} — 🍅 {t.pomodoros_completados}"
                    self.col_doing_timer_list.addItem(texto)

        except Exception as e:
            self.logger.error(f"Erro ao atualizar coluna de tarefas em progresso no timer: {str(e)}", exc_info=True)
