from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt, QRectF, QCoreApplication
from PySide6.QtGui import QPainter, QImage
import os
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def exportar_imagem(self):
    try:
        arquivo, _ = QFileDialog.getSaveFileName(
            self, 
            QCoreApplication.translate("App", "Exportar Mapa"), 
            os.path.join(self.caminho_persistente, "mapa_mental.png"), 
            QCoreApplication.translate("App", "PNG Files (*.png)")
        )

        if arquivo:
            rect = self.scene.itemsBoundingRect()
            image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            image.fill(Qt.white)

            painter = QPainter(image)
            self.scene.render(painter, QRectF(image.rect()), rect)
            painter.end()

            image.save(arquivo)

    except Exception as e:
        logger.error(f"Erro ao exportar imagem: {str(e)}", exc_info=True)
