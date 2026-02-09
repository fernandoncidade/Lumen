from PySide6.QtWidgets import QVBoxLayout, QLabel, QGraphicsEllipseItem, QGraphicsTextItem, QDialog, QTextEdit, QDialogButtonBox
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QColor, QPen, QBrush, QFont
from source.utils.LogManager import LogManager


class NoConceito(QGraphicsEllipseItem):
    def __init__(self, x, y, texto, cor=QColor("#0078d4")):
        super().__init__(-60, -40, 120, 80)
        self.logger = LogManager.get_logger()
        try:
            self.setPos(x, y)
            self.setBrush(QBrush(cor))
            self.setPen(QPen(Qt.black, 2))
            self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
            self.setFlag(QGraphicsEllipseItem.ItemIsSelectable)
            self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)

            self.texto_item = QGraphicsTextItem(texto, self)
            self.texto_item.setDefaultTextColor(Qt.white)
            fonte = QFont("Arial", 11, QFont.Bold)
            self.texto_item.setFont(fonte)

            rect = self.texto_item.boundingRect()
            self.texto_item.setPos(-rect.width()/2, -rect.height()/2)

            self.conexoes = []
            self.texto = texto
            self.cor = cor
            self.notas = ""

        except Exception as e:
            self.logger.error(f"Erro ao inicializar NoConceito: {str(e)}", exc_info=True)

    def itemChange(self, change, value):
        try:
            if change == QGraphicsEllipseItem.ItemPositionHasChanged:
                for linha in self.conexoes:
                    linha.atualizar_posicao()

            return super().itemChange(change, value)

        except Exception as e:
            self.logger.error(f"Erro ao processar mudança de item: {str(e)}", exc_info=True)
            return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        try:
            dialogo = QDialog()
            dialogo.setWindowTitle(QCoreApplication.translate("App", "Editar Conceito"))
            dialogo.setMinimumSize(400, 300)

            layout = QVBoxLayout()

            layout.addWidget(QLabel(QCoreApplication.translate("App", "Texto do Conceito:")))
            input_texto = QTextEdit()
            input_texto.setPlainText(self.texto)
            input_texto.setMaximumHeight(60)
            layout.addWidget(input_texto)

            layout.addWidget(QLabel(QCoreApplication.translate("App", "Notas (Método Feynman - explique com suas palavras):")))
            input_notas = QTextEdit()
            input_notas.setPlainText(self.notas)
            layout.addWidget(input_notas)

            botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            botoes.accepted.connect(dialogo.accept)
            botoes.rejected.connect(dialogo.reject)
            layout.addWidget(botoes)

            dialogo.setLayout(layout)

            if dialogo.exec():
                self.texto = input_texto.toPlainText()
                self.notas = input_notas.toPlainText()
                self.texto_item.setPlainText(self.texto)
                rect = self.texto_item.boundingRect()
                self.texto_item.setPos(-rect.width()/2, -rect.height()/2)

        except Exception as e:
            self.logger.error(f"Erro ao editar conceito: {str(e)}", exc_info=True)
