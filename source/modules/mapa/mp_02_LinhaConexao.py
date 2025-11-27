from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen
from source.utils.LogManager import LogManager


class LinhaConexao(QGraphicsLineItem):
    def __init__(self, no_inicio, no_fim):
        super().__init__()
        self.logger = LogManager.get_logger()
        try:
            self.no_inicio = no_inicio
            self.no_fim = no_fim
            self.setPen(QPen(QColor("#666666"), 3, Qt.SolidLine))

            self.no_inicio.conexoes.append(self)
            self.no_fim.conexoes.append(self)

            self.atualizar_posicao()

        except Exception as e:
            self.logger.error(f"Erro ao inicializar LinhaConexao: {str(e)}", exc_info=True)

    def atualizar_posicao(self):
        try:
            inicio = self.no_inicio.scenePos()
            fim = self.no_fim.scenePos()
            self.setLine(inicio.x(), inicio.y(), fim.x(), fim.y())

        except Exception as e:
            self.logger.error(f"Erro ao atualizar posição da linha: {str(e)}", exc_info=True)
