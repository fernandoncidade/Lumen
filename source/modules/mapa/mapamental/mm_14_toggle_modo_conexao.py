from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def toggle_modo_conexao(self):
    try:
        self.modo_conexao = self.btn_conectar.isChecked()

        if self.modo_conexao:
            self.btn_conectar.setText(QCoreApplication.translate("App", "🔗 Conectar (Ativo)"))
            self.btn_conectar.setStyleSheet("background-color: #28a745; color: white;")
            self.view.setDragMode(QGraphicsView.NoDrag)

        else:
            self.btn_conectar.setText(QCoreApplication.translate("App", "🔗 Conectar Conceitos"))
            self.btn_conectar.setStyleSheet("")
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)
            self.no_origem = None

        self._instalar_handlers_nos()

    except Exception as e:
        logger.error(f"Erro ao alternar modo de conexão: {str(e)}", exc_info=True)
