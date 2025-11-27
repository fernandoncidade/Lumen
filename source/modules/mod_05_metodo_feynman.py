from PySide6.QtWidgets import QWidget
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
from source.utils.GerenciadorBotoesUI import GerenciadorBotoesUI
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
    salvar_conceitos
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

        except Exception as e:
            self.logger.error(f"Erro ao inicializar MetodoFeynman: {str(e)}", exc_info=True)

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
