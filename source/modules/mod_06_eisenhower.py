import os
from PySide6.QtCore import QCoreApplication, Qt, QThread, QObject, Signal, Slot, QTimer
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
from source.language.tr_01_gerenciadorTraducao import GerenciadorTraducao
from source.utils.EventBus import get_event_bus
from source.modules.tempo.tmp_01_Tarefa import Tarefa
from uuid import uuid4
from source.modules.eisenhower.services import (
    init_ui,
    add_placeholder,
    definir_idioma,
    atualizar_textos,
    atualizar_placeholders,
    show_context_menu,
    novo,
    limpar_tudo,
    sair,
    abrir_arquivo,
    salvar_como,
)
from source.modules.eisenhower.ui import (
    add_task,
    handle_item_checked,
    move_item_between_lists,
    remove_task,
    save_tasks,
    load_tasks,
    Calendar,
)
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("App", text)


class EisenhowerMatrixApp(QWidget):
    def __init__(self, gerenciador_traducao=None, embedded=True):
        super().__init__()
        self.embedded = embedded
        if gerenciador_traducao is not None:
            self.gerenciador_traducao = gerenciador_traducao
            self.gerenciador_traducao.idioma_alterado.connect(self.atualizar_textos)

        else:
            self.gerenciador_traducao = GerenciadorTraducao()
            self.gerenciador_traducao.idioma_alterado.connect(self.atualizar_textos)
            self.gerenciador_traducao.aplicar_traducao()

        self.tasks_path = os.path.join(obter_caminho_persistente(), "tasks.json")

        self.initUI()
        self.load_tasks()
        self._integracao_ids_recebidos = set()
        self._setup_integracao_gestao_tempo()

        try:
            class _EisenhowerWorker(QObject):
                request_save = Signal(str, object)
                save_finished = Signal(bool)
                error = Signal(str)

                def __init__(self):
                    super().__init__()
                    self.request_save.connect(self._save)

                @Slot(str, object)
                def _save(self, path, tasks):
                    try:
                        import json, os
                        if not path:
                            self.save_finished.emit(False)
                            return

                        dirp = os.path.dirname(path)
                        if dirp and not os.path.exists(dirp):
                            try:
                                os.makedirs(dirp, exist_ok=True)

                            except Exception:
                                pass

                        with open(path, 'w', encoding='utf-8') as f:
                            json.dump(tasks or {}, f, ensure_ascii=False, indent=2)

                        self.save_finished.emit(True)

                    except Exception as e:
                        self.error.emit(str(e))

            self._eisenhower_thread = QThread()
            self._eisenhower_worker = _EisenhowerWorker()
            self._eisenhower_worker.moveToThread(self._eisenhower_thread)
            self._eisenhower_worker.error.connect(lambda e: logger.error(f"Worker error (Eisenhower): {e}"))
            self._eisenhower_thread.start()

            try:
                app = QCoreApplication.instance()
                if app is not None:
                    app.aboutToQuit.connect(self._stop_eisenhower_thread)

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao iniciar thread do Eisenhower: {e}", exc_info=True)

        if not self.embedded:
            self.criar_menu_configuracoes()

    def criar_menu_configuracoes(self):
        return

    def definir_idioma(self, codigo_idioma):
        definir_idioma(self, codigo_idioma)

    def initUI(self):
        init_ui(self)
        try:
            if hasattr(self, "_root_widget"):
                outer_layout = QHBoxLayout(self)
                outer_layout.setContentsMargins(0, 0, 0, 0)
                outer_layout.setSpacing(0)

                self.calendar_pane = Calendar(self)
                outer_layout.addWidget(self.calendar_pane, 0, Qt.AlignLeft)
                outer_layout.addWidget(self._root_widget, 1)

                self._hide_legacy_calendar_button()

        except Exception as e:
            logger.error(f"Erro ao inicializar UI (embedded): {e}", exc_info=True)

    def _hide_legacy_calendar_button(self):
        try:
            for btn in self.findChildren(QPushButton):
                if btn.text().strip().lower() in {get_text("Calendário").strip().lower(), "calendário", "calendario", "calendar"}:
                    btn.hide()

        except Exception as e:
            logger.error(f"Erro ao ocultar botão legado do calendário: {e}", exc_info=True)

    def add_placeholder(self, list_widget, text):
        add_placeholder(self, list_widget, text)

    def _is_group_header(self, item):
        try:
            return item.data(Qt.UserRole + 1) == "group_header"

        except Exception:
            return False

    def _time_group_label(self, time_str: str) -> str:
        try:
            hh = int((time_str or "0:0").split(":")[0])

        except Exception:
            hh = 0

        return f"{hh:02d}:00–{hh:02d}:59"

    def _time_key(self, time_str: str):
        if not time_str:
            return (999, 999)

        try:
            parts = time_str.split(":")
            return (int(parts[0]), int(parts[1]))

        except Exception:
            return (999, 999)

    def insert_task_into_quadrant_list(self, lst, item):
        data = item.data(Qt.UserRole) or {}
        time_str = data.get("time")
        if not time_str:
            lst.addItem(item)
            return

        if lst.count() == 1 and not (lst.item(0).flags() & Qt.ItemIsSelectable):
            lst.clear()

        label = self._time_group_label(time_str)

        header_index = None
        insert_header_index = None
        existing_headers = []

        for i in range(lst.count()):
            it = lst.item(i)
            if not it:
                continue

            if self._is_group_header(it):
                existing_headers.append((i, it.text()))

        for idx, text in existing_headers:
            if text == label:
                header_index = idx
                break

        if header_index is None:
            try:
                hour = int(label.split(":")[0])

            except Exception:
                hour = 0

            insert_header_index = lst.count()
            for idx, text in existing_headers:
                try:
                    h2 = int(text.split(":")[0])

                except Exception:
                    h2 = 0

                if hour < h2:
                    insert_header_index = idx
                    break

            from PySide6.QtWidgets import QListWidgetItem
            header = QListWidgetItem(label)
            from PySide6.QtCore import Qt as _Qt
            header.setFlags((header.flags() & ~_Qt.ItemIsSelectable) & ~_Qt.ItemIsEnabled)
            header.setData(_Qt.UserRole + 1, "group_header")
            lst.insertItem(insert_header_index, header)
            header_index = insert_header_index

        start = header_index + 1
        end = lst.count()
        for i in range(start, lst.count()):
            it = lst.item(i)
            if it and self._is_group_header(it):
                end = i
                break

        new_key = (self._time_key(time_str), (data.get("text") or item.text()).lower())
        pos = end
        for i in range(start, end):
            it = lst.item(i)
            idata = it.data(Qt.UserRole) or {}
            ikey = (self._time_key(idata.get("time")), (idata.get("text") or it.text()).lower())
            if new_key < ikey:
                pos = i
                break

        lst.insertItem(pos, item)

    def cleanup_time_groups(self, lst):
        i = 0
        from PySide6.QtCore import Qt as _Qt
        while i < lst.count():
            it = lst.item(i)
            if it and self._is_group_header(it):
                if i + 1 >= lst.count() or self._is_group_header(lst.item(i + 1)) or (lst.item(i + 1).flags() & _Qt.ItemIsSelectable) == 0:
                    j = i + 1
                    found_task = False
                    while j < lst.count():
                        it2 = lst.item(j)
                        if self._is_group_header(it2):
                            break

                        if it2.flags() & _Qt.ItemIsSelectable:
                            found_task = True
                            break

                        j += 1

                    if not found_task:
                        lst.takeItem(i)
                        continue

            i += 1

    def add_task(self):
        task_text = ""
        selected_quadrant = 0
        date_iso = None
        time_str = None
        try:
            task_text = (self.task_input.text() or "").strip()
            selected_quadrant = int(self.quadrant_selector.currentIndex())

            if hasattr(self, "date_checkbox") and self.date_checkbox.isChecked():
                try:
                    date_iso = self.date_input.date().toString(Qt.ISODate)

                except Exception:
                    date_iso = None

                if hasattr(self, "time_checkbox") and hasattr(self, "time_input") and self.time_checkbox.isChecked():
                    try:
                        time_str = self.time_input.time().toString("HH:mm")

                    except Exception:
                        time_str = None

        except Exception:
            pass

        add_task(self)
        try:
            if hasattr(self, "calendar_pane") and self.calendar_pane:
                self.calendar_pane.calendar_panel.update_task_list()

            try:
                if hasattr(self, "integrate_time_button") and self.integrate_time_button and self.integrate_time_button.isChecked():
                    if task_text:
                        prioridades = [
                            "Importante e Urgente",
                            "Importante, mas Não Urgente",
                            "Não Importante, mas Urgente",
                            "Não Importante e Não Urgente",
                        ]
                        prioridade = prioridades[selected_quadrant] if 0 <= selected_quadrant < len(prioridades) else "Importante e Urgente"
                        payload = {
                            "integration_id": str(uuid4()),
                            "origin": "eisenhower",
                            "titulo": task_text,
                            "prioridade": Tarefa.normalizar_prioridade(prioridade),
                            "date": date_iso,
                            "time": time_str,
                        }
                        get_event_bus().send_tarefa(payload)

            except Exception as e:
                logger.debug(f"Falha ao enviar tarefa do Eisenhower para Gestão de Tempo: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de tarefas no calendário: {e}", exc_info=True)

    def _setup_integracao_gestao_tempo(self):
        try:
            try:
                if hasattr(self, "integrate_time_button") and self.integrate_time_button:
                    self.integrate_time_button.setToolTip(
                        get_text("Quando ativado, tarefas adicionadas na Matriz também são enviadas para o quadro 📋 A Fazer (Gestão de Tempo).")
                    )

            except Exception:
                pass

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
            logger.debug(f"Falha ao configurar integração Gestão de Tempo: {e}", exc_info=True)

    def _on_event_bus_tarefa(self, dados: dict):
        try:
            payload = dados or {}
            if payload.get("origin") != "tempo":
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

            self._adicionar_tarefa_integrada_do_tempo(titulo=titulo, prioridade=prioridade)

        except Exception as e:
            logger.debug(f"Falha ao receber tarefa do Tempo no Eisenhower: {e}", exc_info=True)

    def _lista_por_prioridade(self, prioridade: str):
        try:
            p = Tarefa.normalizar_prioridade(prioridade)
        except Exception:
            p = "Importante e Urgente"

        if p == "Importante e Urgente":
            return getattr(self, "quadrant1_list", None)

        if p == "Importante, mas Não Urgente":
            return getattr(self, "quadrant2_list", None)

        if p == "Não Importante, mas Urgente":
            return getattr(self, "quadrant3_list", None)

        return getattr(self, "quadrant4_list", None)

    def _adicionar_tarefa_integrada_do_tempo(self, titulo: str, prioridade: str):
        try:
            lst = self._lista_por_prioridade(prioridade)
            if lst is None:
                return

            try:
                for i in range(lst.count()):
                    it = lst.item(i)
                    if not it:
                        continue

                    if not (it.flags() & Qt.ItemIsSelectable):
                        continue

                    data = it.data(Qt.UserRole) or {}
                    base = (data.get("text") or it.text() or "").strip()
                    if base == titulo:
                        return

            except Exception:
                pass

            if lst.count() == 1 and not (lst.item(0).flags() & Qt.ItemIsSelectable):
                lst.clear()

            from PySide6.QtWidgets import QListWidgetItem
            task_item = QListWidgetItem(titulo)
            task_item.setFlags(task_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            task_item.setCheckState(Qt.Unchecked)
            task_item.setData(Qt.UserRole, {"text": titulo, "date": None, "time": None})

            if hasattr(self, "insert_task_into_quadrant_list"):
                self.insert_task_into_quadrant_list(lst, task_item)

            else:
                lst.addItem(task_item)

            try:
                self.save_tasks()

            except Exception:
                pass

            try:
                if hasattr(self, "calendar_pane") and self.calendar_pane:
                    self.calendar_pane.calendar_panel.update_task_list()

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao adicionar tarefa integrada do Tempo: {e}", exc_info=True)

    def handle_item_checked(self, item, source_list, target_list):
        handle_item_checked(self, item, source_list, target_list)

    def move_item_between_lists(self, item, source, target, new_check_state):
        move_item_between_lists(self, item, source, target, new_check_state)

    def remove_task(self, item, list_widget):
        remove_task(self, item, list_widget)
        try:
            self.cleanup_time_groups(list_widget)
            if hasattr(self, "calendar_pane") and self.calendar_pane:
                self.calendar_pane.calendar_panel.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao remover tarefa: {e}", exc_info=True)

    def save_tasks(self):
        try:
            def _list_to_entries(lst):
                entries = []
                if lst is None:
                    return entries

                for i in range(lst.count()):
                    item = lst.item(i)
                    if item.flags() & Qt.ItemIsSelectable:
                        data = item.data(Qt.UserRole) or {}
                        text = data.get("text", item.text())
                        date = data.get("date")
                        time = data.get("time")
                        entries.append({"text": text, "date": date, "time": time})

                return entries

            tasks = {
                "quadrant1": _list_to_entries(getattr(self, 'quadrant1_list', None) or []),
                "quadrant1_completed": _list_to_entries(getattr(self, 'quadrant1_completed_list', None) or []),
                "quadrant2": _list_to_entries(getattr(self, 'quadrant2_list', None) or []),
                "quadrant2_completed": _list_to_entries(getattr(self, 'quadrant2_completed_list', None) or []),
                "quadrant3": _list_to_entries(getattr(self, 'quadrant3_list', None) or []),
                "quadrant3_completed": _list_to_entries(getattr(self, 'quadrant3_completed_list', None) or []),
                "quadrant4": _list_to_entries(getattr(self, 'quadrant4_list', None) or []),
                "quadrant4_completed": _list_to_entries(getattr(self, 'quadrant4_completed_list', None) or []),
            }

            if hasattr(self, '_eisenhower_worker') and getattr(self, '_eisenhower_worker') is not None:
                try:
                    self._eisenhower_worker.request_save.emit(self.tasks_path, tasks)

                except Exception:
                    globals()['save_tasks'](self)

            else:
                globals()['save_tasks'](self)

        except Exception as e:
            logger.error(f"Erro ao salvar tasks via thread: {e}", exc_info=True)

    def load_tasks(self):
        load_tasks(self)
        try:
            if hasattr(self, "calendar_pane") and self.calendar_pane:
                self.calendar_pane.calendar_panel.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao carregar tarefas: {e}", exc_info=True)

    def atualizar_textos(self):
        def _apply_updates():
            try:
                atualizar_textos(self)
                if hasattr(self, "calendar_pane") and self.calendar_pane:
                    self.calendar_pane.on_language_changed()

            except Exception as e:
                logger.error(f"Erro ao atualizar textos: {e}", exc_info=True)

        try:
            QTimer.singleShot(0, _apply_updates)

        except Exception:
            _apply_updates()

    def atualizar_placeholders(self):
        atualizar_placeholders(self)

    def exibir_sobre(self):
        try:
            from source.modules.mod_07_exibir_public import exibir_sobre as _exibir_sobre
            _exibir_sobre(self)

        except Exception as e:
            logger.error(f"Erro ao exibir sobre: {e}", exc_info=True)

    def show_context_menu(self, point, list_widget):
        show_context_menu(self, point, list_widget)

    def open_calendar(self):
        try:
            if hasattr(self, "calendar_pane") and self.calendar_pane:
                self.calendar_pane.toggle_panel(open_if_hidden=True)

        except Exception as e:
            logger.error(f"Erro ao abrir calendário: {e}", exc_info=True)

    def nova_sessao(self):
        novo(self)

    def abrir_arquivo(self):
        abrir_arquivo(self)

    def salvar_como(self):
        salvar_como(self)

    def limpar_tudo(self):
        limpar_tudo(self)

    def sair_app(self):
        sair(self)

    def _stop_eisenhower_thread(self):
        try:
            if hasattr(self, '_eisenhower_thread') and isinstance(self._eisenhower_thread, QThread) and self._eisenhower_thread.isRunning():
                try:
                    self._eisenhower_thread.quit()

                except Exception:
                    pass

                try:
                    self._eisenhower_thread.wait(3000)

                except Exception:
                    pass

        except Exception as e:
            logger.error(f"Erro ao parar thread do Eisenhower: {e}", exc_info=True)

    def cleanup(self):
        try:
            self._stop_eisenhower_thread()

        except Exception:
            pass
