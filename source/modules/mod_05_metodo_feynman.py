from PySide6.QtWidgets import QWidget
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
from source.utils.GerenciadorBotoesUI import GerenciadorBotoesUI
from source.utils.EventBus import get_event_bus
import os
from source.modules.feynman import (
    carregar_conceitos,
    setup_ui,
    atualizar_traducoes,
    novo_conceito,
    limpar_campos,
    salvar_conceito_atual,
    selecionar_conceito,
    deletar_conceito,
    atualizar_lista,
    salvar_conceitos,
    mostrar_menu_contexto,
    redefinir_dominio
)


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

            self.event_bus = get_event_bus()
            self.event_bus.conceito_atualizado.connect(self.receber_conceito_mapa_mental)
            self.logger.info("MetodoFeynman conectado ao EventBus")

        except Exception as e:
            self.logger.error(f"Erro ao inicializar MetodoFeynman: {str(e)}", exc_info=True)

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
                existente['revisao'] = notas
                if not existente.get('explicacao'):
                    existente['explicacao'] = notas

                self.logger.info(f"Conceito '{titulo}' atualizado com notas do Mapa Mental")

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
