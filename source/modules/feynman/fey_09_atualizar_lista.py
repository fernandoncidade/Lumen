from PySide6.QtWidgets import QListWidgetItem
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def atualizar_lista(self):
    try:
        self.lista_conceitos.clear()

        for conceito in self.conceitos:
            emoji = ["🔴", "🟡", "🟢"][conceito['dominio']]
            item = QListWidgetItem(f"{emoji} {conceito['titulo']}")
            self.lista_conceitos.addItem(item)

    except Exception as e:
        logger.error(f"Erro ao atualizar lista de conceitos: {str(e)}", exc_info=True)
