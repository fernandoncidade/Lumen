from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QGraphicsEllipseItem, QGraphicsTextItem, QDialog, 
                               QTextEdit, QDialogButtonBox, QGraphicsDropShadowEffect, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QColor, QPen, QBrush, QFont
from source.utils.LogManager import LogManager
from source.utils.EventBus import get_event_bus


class NoConceito(QGraphicsEllipseItem):
    def __init__(self, x, y, texto, cor=QColor("#0078d4")):
        super().__init__(-60, -40, 120, 80)
        self.logger = LogManager.get_logger()
        try:
            self.setPos(x, y)
            self.setBrush(QBrush(QColor(cor.red(), cor.green(), cor.blue(), 185)))
            self.setPen(QPen(QColor(255, 255, 255, 28), 2))
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 3)
            shadow.setColor(QColor(0, 0, 0, 140))
            self.setGraphicsEffect(shadow)

            self.texto_item = QGraphicsTextItem(texto, self)
            self.texto_item.setDefaultTextColor(QColor(245, 245, 245))
            fonte = QFont("Segoe UI", 11, QFont.Bold)
            self.texto_item.setFont(fonte)
            rect = self.texto_item.boundingRect()
            self.texto_item.setPos(-rect.width()/2, -rect.height()/2)

            self._badge = QGraphicsEllipseItem(-4, -34, 8, 8, self)
            self._badge.setBrush(QBrush(QColor("#ffb900")))
            self._badge.setPen(QPen(Qt.NoPen))
            self._badge.setVisible(False)

            self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
            self.setFlag(QGraphicsEllipseItem.ItemIsSelectable)
            self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)

            self.conexoes = []
            self.texto = texto
            self.cor = cor
            self.notas = ""
            self.info_associada: list[str] = []

            self.event_bus = get_event_bus()

        except Exception as e:
            self.logger.error(f"Erro ao inicializar NoConceito: {str(e)}", exc_info=True)

    def itemChange(self, change, value):
        try:
            if change == QGraphicsEllipseItem.ItemPositionHasChanged:
                for linha in self.conexoes:
                    linha.atualizar_posicao()

                scene = self.scene()
                if scene and hasattr(scene, "snap"):
                    snapped = scene.snap(self.pos())
                    super().setPos(snapped)

            return super().itemChange(change, value)

        except Exception as e:
            self.logger.error(f"Erro ao processar mudança de item: {str(e)}", exc_info=True)
            return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self.setPen(QPen(QColor(255, 255, 255, 80), 3))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setPen(QPen(QColor(255, 255, 255, 28), 2))
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        try:
            dialogo = QDialog()
            dialogo.setWindowTitle(QCoreApplication.translate("App", "Editar Conceito"))
            dialogo.setMinimumSize(560, 460)

            layout = QVBoxLayout()

            layout.addWidget(QLabel(QCoreApplication.translate("App", "Texto do Conceito:")))
            input_texto = QTextEdit()
            input_texto.setPlainText(self.texto)
            input_texto.setMaximumHeight(60)
            layout.addWidget(input_texto)

            layout.addWidget(QLabel(QCoreApplication.translate("App", "Informações associadas:")))
            info_view = QTextEdit()
            info_view.setReadOnly(True)

            if self.info_associada:
                info_view.setPlainText("\n\n".join(self.info_associada))

            else:
                info_view.setPlainText(QCoreApplication.translate("App", "Sem informações associadas."))

            layout.addWidget(info_view)

            layout.addWidget(QLabel(QCoreApplication.translate("App", "Notas (Método Feynman - explique com suas palavras):")))
            input_notas = QTextEdit()
            input_notas.setPlainText(self.notas)
            layout.addWidget(input_notas)

            layout_botoes = QHBoxLayout()

            btn_integrar_feynman = QPushButton(QCoreApplication.translate("App", "➕ Integrar ao Método Feynman"))
            btn_integrar_feynman.setToolTip(QCoreApplication.translate("App", "Envia as notas para o Método Feynman"))
            layout_botoes.addWidget(btn_integrar_feynman)

            botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            botoes.accepted.connect(dialogo.accept)
            botoes.rejected.connect(dialogo.reject)
            layout_botoes.addWidget(botoes)

            layout.addLayout(layout_botoes)

            dialogo.setLayout(layout)

            def integrar_ao_feynman():
                try:
                    titulo = input_texto.toPlainText().strip()
                    notas_texto = input_notas.toPlainText().strip()

                    if not titulo:
                        QMessageBox.warning(
                            dialogo,
                            QCoreApplication.translate("App", "Atenção"),
                            QCoreApplication.translate("App", "Por favor, digite o título do conceito!")
                        )
                        return

                    if not notas_texto:
                        QMessageBox.warning(
                            dialogo,
                            QCoreApplication.translate("App", "Atenção"),
                            QCoreApplication.translate("App", "Por favor, escreva suas notas antes de integrar ao Método Feynman!")
                        )
                        return

                    dados = {'titulo': titulo, 'notas': notas_texto}
                    self.event_bus.conceito_atualizado.emit(dados)
                    self.logger.info(f"Conceito '{titulo}' integrado ao Método Feynman via botão específico")

                    QMessageBox.information(
                        dialogo,
                        QCoreApplication.translate("App", "✅ Integrado"),
                        QCoreApplication.translate("App", "Conceito '{titulo}' integrado ao Método Feynman com sucesso!").format(titulo=titulo)
                    )

                except Exception as e:
                    self.logger.error(f"Erro ao integrar conceito ao Método Feynman: {str(e)}", exc_info=True)
                    QMessageBox.critical(
                        dialogo,
                        QCoreApplication.translate("App", "Erro"),
                        QCoreApplication.translate("App", "Erro ao integrar ao Método Feynman: {erro}").format(erro=str(e))
                    )

            btn_integrar_feynman.clicked.connect(integrar_ao_feynman)

            if dialogo.exec():
                self.texto = input_texto.toPlainText().strip()
                self.notas = input_notas.toPlainText().strip()
                self.texto_item.setPlainText(self.texto)
                rect = self.texto_item.boundingRect()
                self.texto_item.setPos(-rect.width()/2, -rect.height()/2)
                self._badge.setVisible(bool(self.notas))
                self.logger.debug(f"Conceito '{self.texto}' atualizado localmente (OK) - SEM integração ao Feynman")

        except Exception as e:
            self.logger.error(f"Erro ao editar conceito: {str(e)}", exc_info=True)
