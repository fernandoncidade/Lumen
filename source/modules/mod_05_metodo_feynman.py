from PySide6.QtWidgets import QWidget
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
from source.utils.GerenciadorBotoesUI import GerenciadorBotoesUI
from source.utils.EventBus import get_event_bus
import os
from source.modules.feynman import (carregar_conceitos, setup_ui, atualizar_traducoes, 
                                    novo_conceito, limpar_campos, salvar_conceito_atual, 
                                    selecionar_conceito, deletar_conceito, atualizar_lista, 
                                    salvar_conceitos, mostrar_menu_contexto, redefinir_dominio)


class MetodoFeynman(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LogManager.get_logger()
        try:
            caminho_persistente = obter_caminho_persistente()
            self.arquivo_conceitos = os.path.join(caminho_persistente, "conceitos_feynman.json")
            self.conceitos = carregar_conceitos(self)
            self.gerenciador_botoes = GerenciadorBotoesUI(self)
            setup_ui(self)

            from PySide6.QtCore import QThread, QObject, Signal, Slot, QCoreApplication

            self.event_bus = get_event_bus()
            self.event_bus.conceito_atualizado.connect(self.receber_conceito_mapa_mental)

            try:
                self.event_bus.drain_pending_conceitos()

            except Exception:
                pass

            self.logger.info("MetodoFeynman conectado ao EventBus")

        except Exception as e:
            self.logger.error(f"Erro ao inicializar MetodoFeynman: {str(e)}", exc_info=True)


        class FeynmanWorker(QObject):
            request_load = Signal(str)
            request_save = Signal(str, object)
            conceitos_loaded = Signal(object)
            save_finished = Signal(bool)
            error = Signal(str)

            def __init__(self):
                super().__init__()
                self.request_load.connect(self._load)
                self.request_save.connect(self._save)

            @Slot(str)
            def _load(self, arquivo_conceitos):
                try:
                    import os, json
                    if arquivo_conceitos and os.path.exists(arquivo_conceitos):
                        with open(arquivo_conceitos, 'r', encoding='utf-8') as f:
                            dados = json.load(f)
                            self.conceitos_loaded.emit(dados if isinstance(dados, list) else [])

                    else:
                        self.conceitos_loaded.emit([])

                except Exception as e:
                    self.error.emit(str(e))

            @Slot(str, object)
            def _save(self, arquivo_conceitos, conceitos):
                try:
                    import json, os
                    if not arquivo_conceitos:
                        self.save_finished.emit(False)
                        return

                    dirp = os.path.dirname(arquivo_conceitos)
                    if dirp and not os.path.exists(dirp):
                        try:
                            os.makedirs(dirp, exist_ok=True)

                        except Exception:
                            pass

                    with open(arquivo_conceitos, 'w', encoding='utf-8') as f:
                        json.dump(conceitos or [], f, ensure_ascii=False, indent=4)

                    self.save_finished.emit(True)

                except Exception as e:
                    self.error.emit(str(e))

        try:
            self._feynman_thread = QThread()
            self._feynman_worker = FeynmanWorker()
            self._feynman_worker.moveToThread(self._feynman_thread)
            self._feynman_worker.conceitos_loaded.connect(self._on_conceitos_loaded)
            self._feynman_worker.save_finished.connect(lambda ok: None)
            self._feynman_worker.error.connect(lambda e: self.logger.error(f"Worker error (Feynman): {e}"))
            self._feynman_thread.start()

            def _carregar_conceitos_via_worker():
                try:
                    arquivo = getattr(self, 'arquivo_conceitos', None)
                    self._feynman_worker.request_load.emit(arquivo)

                except Exception as e:
                    self.logger.error(f"Erro ao solicitar carregamento de conceitos: {e}", exc_info=True)

            def _salvar_conceitos_via_worker():
                try:
                    arquivo = getattr(self, 'arquivo_conceitos', None)
                    self._feynman_worker.request_save.emit(arquivo, getattr(self, 'conceitos', []))

                except Exception as e:
                    self.logger.error(f"Erro ao solicitar salvamento de conceitos: {e}", exc_info=True)

            self.carregar_conceitos = _carregar_conceitos_via_worker
            self.salvar_conceitos = _salvar_conceitos_via_worker

            try:
                app = QCoreApplication.instance()
                if app is not None:
                    app.aboutToQuit.connect(self._stop_feynman_thread)

            except Exception:
                pass

        except Exception as e:
            self.logger.error(f"Erro ao iniciar thread do Método Feynman: {e}", exc_info=True)

    def receber_conceito_mapa_mental(self, dados: dict):
        try:
            titulo = dados.get('titulo', '').strip()
            notas = dados.get('notas', '').strip()

            if not titulo:
                self.logger.warning("Título vazio recebido do Mapa Mental, ignorando")
                return

            if not notas:
                self.logger.warning(f"Notas vazias para conceito '{titulo}', ignorando")
                return

            self.logger.info(f"Recebendo conceito do Mapa Mental para integração: '{titulo}'")

            existente = next((c for c in self.conceitos if c.get('titulo') == titulo), None)

            if existente:
                # Sempre atualizar revisão com as notas mais recentes
                existente['revisao'] = notas

                # Se explicação estiver vazia, preenche; caso contrário, anexa as novas notas
                exp = existente.get('explicacao', '') or ''
                if not exp.strip():
                    existente['explicacao'] = notas

                else:
                    # Evita duplicação exata: anexa somente se diferente
                    if notas.strip() and notas.strip() not in exp:
                        existente['explicacao'] = exp + "\n\n" + notas

                self.logger.info(f"Conceito '{titulo}' atualizado com notas do Mapa Mental (merge/append)")

            else:
                novo = {
                    'titulo': titulo,
                    'explicacao': notas,
                    'lacunas': '',
                    'revisao': notas,
                    'dominio': 0
                }
                self.conceitos.append(novo)
                self.logger.info(f"Novo conceito '{titulo}' criado a partir do Mapa Mental")

            self.salvar_conceitos()
            self.atualizar_lista()

            self.logger.info(f"Conceito '{titulo}' integrado e lista atualizada")

        except Exception as e:
            self.logger.error(f"Erro ao receber conceito do Mapa Mental: {str(e)}", exc_info=True)

    def atualizar_traducoes(self):
        atualizar_traducoes(self)

    def novo_conceito(self):
        novo_conceito(self)

    def limpar_campos(self):
        limpar_campos(self)

    def salvar_conceito_atual(self):
        salvar_conceito_atual(self)

    def selecionar_conceito(self, item):
        selecionar_conceito(self, item)

    def deletar_conceito(self):
        deletar_conceito(self)

    def atualizar_lista(self):
        atualizar_lista(self)

    def salvar_conceitos(self):
        salvar_conceitos(self)

    def mostrar_menu_contexto(self, position):
        mostrar_menu_contexto(self, position)

    def redefinir_dominio(self, item, novo_nivel):
        redefinir_dominio(self, item, novo_nivel)

    def _on_conceitos_loaded(self, conceitos):
        try:
            self.conceitos = conceitos or []
            try:
                if hasattr(self, 'atualizar_lista'):
                    self.atualizar_lista()

            except Exception:
                pass

        except Exception as e:
            self.logger.error(f"Erro ao processar conceitos carregados: {e}", exc_info=True)

    def _stop_feynman_thread(self):
        try:
            if hasattr(self, '_feynman_thread') and self._feynman_thread.isRunning():
                self._feynman_thread.quit()
                self._feynman_thread.wait(3000)

        except Exception as e:
            self.logger.error(f"Erro ao parar thread do Método Feynman: {e}", exc_info=True)

    def cleanup(self):
        try:
            self._stop_feynman_thread()

        except Exception:
            pass
