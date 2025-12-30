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

        msg = QMessageBox(self)
        msg.setWindowTitle(QCoreApplication.translate("App", "Confirmar Exclusão"))
        msg.setText(QCoreApplication.translate("App", "Deseja realmente deletar o conceito '{titulo}'?").format(titulo=titulo))
        btn_yes = msg.addButton(QCoreApplication.translate("App", "Yes"), QMessageBox.YesRole)
        btn_no = msg.addButton(QCoreApplication.translate("App", "No"), QMessageBox.NoRole)
        msg.exec()

        if msg.clickedButton() == btn_yes:
            self.conceitos = [c for c in self.conceitos if c['titulo'] != titulo]
            self.salvar_conceitos()
            self.atualizar_lista()
            self.limpar_campos()

    except Exception as e:
        logger.error(f"Erro ao deletar conceito: {str(e)}", exc_info=True)
