from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, 
                               QListWidgetItem, QComboBox, QGroupBox, QMessageBox, QMenu, QInputDialog)
from PySide6.QtCore import Qt, Signal, QCoreApplication
from PySide6.QtGui import QAction
import json
import os
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
from source.modules.tempo.tmp_01_Tarefa import Tarefa


class GerenciadorTarefas(QWidget):
    listas_atualizadas = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LogManager.get_logger()
        try:
            caminho_persistente = obter_caminho_persistente()
            self.arquivo_tarefas = os.path.join(caminho_persistente, "tarefas.json")
            self.tarefas = self.carregar_tarefas()
            self.setup_ui()

        except Exception as e:
            self.logger.error(f"Erro ao inicializar GerenciadorTarefas: {str(e)}", exc_info=True)

    def carregar_tarefas(self):
        tarefas = []
        try:
            if os.path.exists(self.arquivo_tarefas):
                with open(self.arquivo_tarefas, "r", encoding="utf-8") as f:
                    data = json.load(f)

                bruto = data.get("tarefas") if isinstance(data, dict) else data
                if isinstance(bruto, list):
                    for item in bruto:
                        t = Tarefa.from_dict(item)
                        if t:
                            tarefas.append(t)

            return tarefas

        except Exception as e:
            self.logger.error(f"Erro ao carregar tarefas: {str(e)}", exc_info=True)
            return []

    def salvar_tarefas(self):
        try:
            os.makedirs(os.path.dirname(self.arquivo_tarefas), exist_ok=True)
            with open(self.arquivo_tarefas, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in self.tarefas], f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"Erro ao salvar tarefas: {str(e)}", exc_info=True)

    def setup_ui(self):
        try:
            layout = QVBoxLayout()

            adicionar = QHBoxLayout()

            self.input_tarefa = QLineEdit()
            self.input_tarefa.returnPressed.connect(self.adicionar_tarefa)
            adicionar.addWidget(self.input_tarefa)

            self.combo_prioridade = QComboBox()
            adicionar.addWidget(self.combo_prioridade)

            self.btn_adicionar = QPushButton()
            self.btn_adicionar.clicked.connect(self.adicionar_tarefa)
            adicionar.addWidget(self.btn_adicionar)

            self.btn_mover = QPushButton()
            self.btn_mover.clicked.connect(self.mover_tarefas_marcadas)
            adicionar.addWidget(self.btn_mover)

            self.btn_remover = QPushButton()
            self.btn_remover.clicked.connect(self.remover_tarefas_marcadas)
            adicionar.addWidget(self.btn_remover)

            self.btn_resetar_contagem = QPushButton()
            self.btn_resetar_contagem.clicked.connect(self.resetar_contagem_botao)
            adicionar.addWidget(self.btn_resetar_contagem)

            layout.addLayout(adicionar)

            kanban = QHBoxLayout()
            self.col_todo = self.criar_coluna("Todo")
            kanban.addWidget(self.col_todo)

            self.col_doing = self.criar_coluna("Doing")
            kanban.addWidget(self.col_doing)

            self.col_done = self.criar_coluna("Done")
            kanban.addWidget(self.col_done)

            layout.addLayout(kanban)

            self.setLayout(layout)
            self.atualizar_traducoes()
            self.atualizar_listas()

        except Exception as e:
            self.logger.error(f"Erro ao configurar interface do GerenciadorTarefas: {str(e)}", exc_info=True)

    def atualizar_traducoes(self):
        try:
            self.input_tarefa.setPlaceholderText(
                QCoreApplication.translate("App", "Digite uma nova tarefa... (Ex: 'Estudar Resistência dos Materiais - Cap 3')")
            )

            self.combo_prioridade.clear()
            self.combo_prioridade.addItems([
                QCoreApplication.translate("App", "🔴 Alta"),
                QCoreApplication.translate("App", "🟡 Média"),
                QCoreApplication.translate("App", "🟢 Baixa")
            ])
            self.combo_prioridade.setCurrentText(QCoreApplication.translate("App", "🟡 Média"))
            self._ajustar_largura_combo(self.combo_prioridade)

            self.btn_adicionar.setText(QCoreApplication.translate("App", "➕ Adicionar"))
            self.btn_remover.setText(QCoreApplication.translate("App", "🗑️ Remover Tarefa(s)"))
            self.btn_mover.setText(QCoreApplication.translate("App", "🔀 Mover Tarefa(s)"))

            if hasattr(self, 'btn_resetar_contagem'):
                self.btn_resetar_contagem.setText(QCoreApplication.translate("App", "🔄 Resetar Contagem"))

            self.col_todo.setTitle(QCoreApplication.translate("App", "📋 A Fazer"))
            self.col_doing.setTitle(QCoreApplication.translate("App", "⚙️ Em Progresso"))
            self.col_done.setTitle(QCoreApplication.translate("App", "✅ Concluído"))

        except Exception as e:
            self.logger.error(f"Erro ao atualizar traduções do GerenciadorTarefas: {str(e)}", exc_info=True)

    def criar_coluna(self, status):
        try:
            grupo = QGroupBox()
            layout = QVBoxLayout()

            lista = QListWidget()
            lista.setDragDropMode(QListWidget.InternalMove)
            lista.itemDoubleClicked.connect(lambda item: self.mover_tarefa(item, status))

            lista.setContextMenuPolicy(Qt.CustomContextMenu)
            lista.customContextMenuRequested.connect(lambda pos, l=lista: self.mostrar_menu_contexto(pos, l))

            try:
                model = lista.model()
                model.rowsMoved.connect(lambda *args, l=lista: self._on_rows_moved(l))

            except Exception:
                pass

            layout.addWidget(lista)
            grupo.setLayout(layout)

            grupo.lista = lista
            grupo.status = status

            return grupo

        except Exception as e:
            self.logger.error(f"Erro ao criar coluna '{status}': {str(e)}", exc_info=True)
            return QGroupBox()

    def _on_rows_moved(self, lista):
        try:
            self._sincronizar_status_pos_movimento()

        except Exception as e:
            self.logger.error(f"Erro ao tratar rowsMoved: {e}", exc_info=True)

    def _sincronizar_status_pos_movimento(self):
        try:
            if not hasattr(self, 'tarefas'):
                return

            mapping = {}

            try:
                mapping[self.col_todo.lista] = "Todo"
                mapping[self.col_doing.lista] = "Doing"
                mapping[self.col_done.lista] = "Done"

            except Exception:
                return

            alterou = False

            for lst, status in mapping.items():
                for i in range(lst.count()):
                    it = lst.item(i)
                    if not it:
                        continue

                    tid = it.data(Qt.UserRole)
                    titulo = it.text().split('\n')[0].replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')

                    for t in self.tarefas:
                        if (tid and getattr(t, 'id', None) == tid) or (not tid and t.titulo == titulo):
                            if getattr(t, 'status', None) != status:
                                t.status = status
                                alterou = True

                            break

            if alterou:
                self.salvar_tarefas()

        except Exception as e:
            self.logger.error(f"Erro ao sincronizar status após movimento: {str(e)}", exc_info=True)

    def adicionar_tarefa(self):
        try:
            titulo = self.input_tarefa.text().strip()
            if not titulo:
                return

            idx = self.combo_prioridade.currentIndex()
            prioridades = ["Alta", "Média", "Baixa"]
            prioridade = prioridades[idx] if 0 <= idx < len(prioridades) else "Média"

            tarefa = Tarefa(titulo, prioridade=prioridade)
            self.tarefas.append(tarefa)

            self.input_tarefa.clear()
            self.salvar_tarefas()
            self.atualizar_listas()

        except Exception as e:
            self.logger.error(f"Erro ao adicionar tarefa: {str(e)}", exc_info=True)

    def mover_tarefa(self, item, status_atual):
        try:
            tarefa_id = item.data(Qt.UserRole)
            alvo = None
            for tarefa in self.tarefas:
                if getattr(tarefa, 'id', None) == tarefa_id:
                    alvo = tarefa
                    break

            if not alvo:
                texto = item.text().split('\n')[0].replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')
                for tarefa in self.tarefas:
                    if tarefa.titulo == texto:
                        alvo = tarefa
                        break

            if not alvo:
                return

            if status_atual == "Todo":
                alvo.status = "Doing"

            elif status_atual == "Doing":
                alvo.status = "Done"

            else:
                alvo.status = "Todo"

            self.salvar_tarefas()
            self.atualizar_listas()

        except Exception as e:
            self.logger.error(f"Erro ao mover tarefa: {str(e)}", exc_info=True)

    def atualizar_listas(self):
        try:
            self.col_todo.lista.clear()
            self.col_doing.lista.clear()
            self.col_done.lista.clear()

            for tarefa in self.tarefas:
                prioridade_norm = Tarefa.normalizar_prioridade(getattr(tarefa, 'prioridade', 'Média'))
                emoji = {"Alta": "🔴", "Média": "🟡", "Baixa": "🟢"}.get(prioridade_norm, "🟡")
                pomodoros_texto = QCoreApplication.translate("App", "🍅 {n} pomodoros").format(n=tarefa.pomodoros_completados)
                texto = f"{emoji} {tarefa.titulo}\n{pomodoros_texto}"

                item = QListWidgetItem(texto)

                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, getattr(tarefa, 'id', None))

                if tarefa.status == "Todo":
                    self.col_todo.lista.addItem(item)

                elif tarefa.status == "Doing":
                    self.col_doing.lista.addItem(item)

                else:
                    self.col_done.lista.addItem(item)

            self.listas_atualizadas.emit()

        except Exception as e:
            self.logger.error(f"Erro ao atualizar listas de tarefas: {str(e)}", exc_info=True)

    def mostrar_menu_contexto(self, pos, lista):
        try:
            item = lista.itemAt(pos)
            if not item:
                return

            menu = QMenu(lista)

            ac_mover_unico = QAction(QCoreApplication.translate("App", "🔀 Mover Tarefa"), self)
            ac_mover_unico.triggered.connect(lambda: self.mover_tarefa_por_item(item))
            menu.addAction(ac_mover_unico)

            if self._ha_tarefas_marcadas():
                ac_mover_marcadas = QAction(QCoreApplication.translate("App", "🔀 Mover Tarefa(s) Marcadas"), self)
                ac_mover_marcadas.triggered.connect(self.mover_tarefas_marcadas)
                menu.addAction(ac_mover_marcadas)

            ac_remover = QAction(QCoreApplication.translate("App", "🗑️ Remover Tarefa"), self)
            ac_remover.triggered.connect(lambda: self.remover_tarefa_por_item(item))
            menu.addAction(ac_remover)

            if self._ha_tarefas_marcadas():
                ac_remover_marcadas = QAction(QCoreApplication.translate("App", "🗑️ Remover Tarefa(s) Marcadas"), self)
                ac_remover_marcadas.triggered.connect(self.remover_tarefas_marcadas)
                menu.addAction(ac_remover_marcadas)

            menu.exec(lista.mapToGlobal(pos))

        except Exception as e:
            self.logger.error(f"Erro ao exibir menu de contexto: {str(e)}", exc_info=True)

    def _ha_tarefas_marcadas(self):
        try:
            for lst in (self.col_todo.lista, self.col_doing.lista, self.col_done.lista):
                for i in range(lst.count()):
                    if lst.item(i).checkState() == Qt.Checked:
                        return True

            return False

        except Exception:
            return False

    def remover_tarefa_por_item(self, item):
        try:
            tarefa_id = item.data(Qt.UserRole)
            if tarefa_id:
                self.tarefas = [t for t in self.tarefas if getattr(t, 'id', None) != tarefa_id]

            else:
                titulo = item.text().split('\n')[0].replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')
                self.tarefas = [t for t in self.tarefas if t.titulo != titulo]

            self.salvar_tarefas()
            self.atualizar_listas()

        except Exception as e:
            self.logger.error(f"Erro ao remover tarefa pelo menu de contexto: {str(e)}", exc_info=True)

    def remover_tarefas_marcadas(self):
        try:
            ids_para_remover = set()
            titulos_para_remover = set()

            for lista in (self.col_todo.lista, self.col_doing.lista, self.col_done.lista):
                for i in range(lista.count()):
                    it = lista.item(i)
                    if it.checkState() == Qt.Checked:
                        tid = it.data(Qt.UserRole)
                        if tid:
                            ids_para_remover.add(tid)

                        else:
                            titulo = it.text().split('\n')[0].replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')
                            titulos_para_remover.add(titulo)

            if not ids_para_remover and not titulos_para_remover:
                return

            novas = []
            for t in self.tarefas:
                if getattr(t, 'id', None) in ids_para_remover:
                    continue

                if t.titulo in titulos_para_remover:
                    continue

                novas.append(t)

            self.tarefas = novas
            self.salvar_tarefas()
            self.atualizar_listas()

        except Exception as e:
            self.logger.error(f"Erro ao remover tarefas marcadas: {str(e)}", exc_info=True)

    def resetar_contagem_botao(self):
        try:
            escopos = [
                QCoreApplication.translate("App", "🔹 Uma tarefa específica"),
                QCoreApplication.translate("App", "📂 Todas as tarefas de uma coluna"),
                QCoreApplication.translate("App", "🌐 Todas as tarefas (global)")
            ]

            escopo, ok = QInputDialog.getItem(
                self,
                QCoreApplication.translate("App", "🔄 Resetar Contagem"),
                QCoreApplication.translate("App", "O que deseja restaurar?"),
                escopos,
                0,
                False
            )
            if not ok or not escopo:
                return

            opcoes_colunas = [
                QCoreApplication.translate("App", "📋 A Fazer"),
                QCoreApplication.translate("App", "⚙️ Em Progresso"),
                QCoreApplication.translate("App", "✅ Concluído")
            ]
            mapa_status = {
                QCoreApplication.translate("App", "📋 A Fazer"): "Todo",
                QCoreApplication.translate("App", "⚙️ Em Progresso"): "Doing",
                QCoreApplication.translate("App", "✅ Concluído"): "Done"
            }

            if escopo == escopos[0]:
                coluna_exibida, ok = QInputDialog.getItem(
                    self,
                    QCoreApplication.translate("App", "🔄 Resetar Contagem"),
                    QCoreApplication.translate("App", "Selecione a coluna:"),
                    opcoes_colunas,
                    0,
                    False
                )
                if not ok or not coluna_exibida:
                    return

                status_coluna = mapa_status.get(coluna_exibida, "Todo")
                tarefas_coluna = [t for t in self.tarefas if getattr(t, 'status', '') == status_coluna]

                if not tarefas_coluna:
                    QMessageBox.information(
                        self,
                        QCoreApplication.translate("App", "Nenhuma tarefa"),
                        QCoreApplication.translate("App", "Não há tarefas nesta coluna.")
                    )
                    return

                titulos = [t.titulo for t in tarefas_coluna]
                titulo_escolhido, ok = QInputDialog.getItem(
                    self,
                    QCoreApplication.translate("App", "🔄 Resetar Contagem"),
                    QCoreApplication.translate("App", "Selecione a tarefa:"),
                    titulos,
                    0,
                    False
                )
                if not ok or not titulo_escolhido:
                    return

                for t in tarefas_coluna:
                    if t.titulo == titulo_escolhido:
                        t.pomodoros_completados = 0
                        break

            elif escopo == escopos[1]:
                coluna_exibida, ok = QInputDialog.getItem(
                    self,
                    QCoreApplication.translate("App", "🔄 Resetar Contagem"),
                    QCoreApplication.translate("App", "Selecione a coluna:"),
                    opcoes_colunas,
                    0,
                    False
                )
                if not ok or not coluna_exibida:
                    return

                status_coluna = mapa_status.get(coluna_exibida, "Todo")
                tarefas_coluna = [t for t in self.tarefas if getattr(t, 'status', '') == status_coluna]

                if not tarefas_coluna:
                    QMessageBox.information(
                        self,
                        QCoreApplication.translate("App", "Nenhuma tarefa"),
                        QCoreApplication.translate("App", "Não há tarefas nesta coluna.")
                    )
                    return

                for t in tarefas_coluna:
                    t.pomodoros_completados = 0

            else:
                if not self.tarefas:
                    QMessageBox.information(
                        self,
                        QCoreApplication.translate("App", "Nenhuma tarefa"),
                        QCoreApplication.translate("App", "Não há tarefas em nenhuma coluna.")
                    )
                    return

                for t in self.tarefas:
                    t.pomodoros_completados = 0

            self.salvar_tarefas()
            self.atualizar_listas()

        except Exception as e:
            self.logger.error(f"Erro ao resetar contagem: {str(e)}", exc_info=True)

    def mover_tarefas_marcadas(self):
        try:
            selecionados = []
            for lista in (self.col_todo.lista, self.col_doing.lista, self.col_done.lista):
                for i in range(lista.count()):
                    it = lista.item(i)
                    if it.checkState() == Qt.Checked:
                        tid = it.data(Qt.UserRole)
                        titulo = it.text().split('\n')[0].replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')
                        selecionados.append((tid, titulo))

            if not selecionados:
                return

            opcoes = [
                QCoreApplication.translate("App", "📋 A Fazer"),
                QCoreApplication.translate("App", "⚙️ Em Progresso"),
                QCoreApplication.translate("App", "✅ Concluído")
            ]
            destino_exibido, ok = QInputDialog.getItem(
                self,
                QCoreApplication.translate("App", "Mover Tarefas"),
                QCoreApplication.translate("App", "Selecione a coluna de destino:"),
                opcoes,
                0,
                False
            )
            if not ok or not destino_exibido:
                return

            mapa_destino = {
                QCoreApplication.translate("App", "📋 A Fazer"): "Todo",
                QCoreApplication.translate("App", "⚙️ Em Progresso"): "Doing",
                QCoreApplication.translate("App", "✅ Concluído"): "Done"
            }
            status_destino = mapa_destino.get(destino_exibido, "Todo")

            ids_set = {tid for tid, _ in selecionados if tid}
            titulos_set = {titulo for tid, titulo in selecionados if not tid}

            for tarefa in self.tarefas:
                if getattr(tarefa, 'id', None) in ids_set or tarefa.titulo in titulos_set:
                    tarefa.status = status_destino

            self.salvar_tarefas()
            self.atualizar_listas()

        except Exception as e:
            self.logger.error(f"Erro ao remover tarefas marcadas: {str(e)}", exc_info=True)

    def mover_tarefa_por_item(self, item):
        try:
            if not item:
                return

            tarefa_id = item.data(Qt.UserRole)
            titulo_item = item.text().split('\n')[0].replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')

            alvo = None
            for t in self.tarefas:
                if (tarefa_id and getattr(t, 'id', None) == tarefa_id) or (t.titulo == titulo_item):
                    alvo = t
                    break

            if not alvo:
                return

            opcoes = [
                QCoreApplication.translate("App", "📋 A Fazer"),
                QCoreApplication.translate("App", "⚙️ Em Progresso"),
                QCoreApplication.translate("App", "✅ Concluído")
            ]

            destino_exibido, ok = QInputDialog.getItem(
                self,
                QCoreApplication.translate("App", "Mover Tarefa"),
                QCoreApplication.translate("App", "Selecione a coluna de destino:"),
                opcoes,
                0,
                False
            )

            if not ok or not destino_exibido:
                return

            mapa_destino = {
                QCoreApplication.translate("App", "📋 A Fazer"): "Todo",
                QCoreApplication.translate("App", "⚙️ Em Progresso"): "Doing",
                QCoreApplication.translate("App", "✅ Concluído"): "Done"
            }
            alvo.status = mapa_destino.get(destino_exibido, "Todo")

            self.salvar_tarefas()
            self.atualizar_listas()

        except Exception as e:
            self.logger.error(f"Erro ao mover tarefa por item (menu): {str(e)}", exc_info=True)

    def _ajustar_largura_combo(self, combo: QComboBox, padding_extra: int = 42, max_visiveis: int = 6):
        try:
            fm = combo.fontMetrics()
            max_width = 0
            for i in range(combo.count()):
                txt = combo.itemText(i)
                max_width = max(max_width, fm.horizontalAdvance(txt))

            largura = max_width + padding_extra
            combo.setFixedWidth(largura)
            combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            combo.setMaxVisibleItems(max_visiveis)

            view = combo.view()
            if view is not None:
                view.setMinimumWidth(largura)

        except Exception as e:
            self.logger.error(f"Erro ao ajustar largura do combo: {str(e)}", exc_info=True)
