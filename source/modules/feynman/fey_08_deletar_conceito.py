from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def deletar_conceito(self):
    try:
        item_atual = self.lista_conceitos.currentItem()
        if not item_atual:
            return

        titulo = item_atual.text().split(' - ')[0].replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')

        resposta = QMessageBox.question(
            self, 
            QCoreApplication.translate("App", "Confirmar Exclusão"), 
            QCoreApplication.translate("App", "Deseja realmente deletar o conceito '{titulo}'?").format(titulo=titulo),
            QMessageBox.Yes | QMessageBox.No
        )

        if resposta == QMessageBox.Yes:
            self.conceitos = [c for c in self.conceitos if c['titulo'] != titulo]
            self.salvar_conceitos()
            self.atualizar_lista()
            self.limpar_campos()

    except Exception as e:
        logger.error(f"Erro ao deletar conceito: {str(e)}", exc_info=True)
