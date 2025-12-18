from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import QCoreApplication, QPointF
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_01_NoConceito import NoConceito
from source.modules.mapa.mp_03_MapaMental import MapaScene

logger = LogManager.get_logger()

def adicionar_no(self):
    try:
        texto, ok = QInputDialog.getText(
            self, 
            QCoreApplication.translate("App", "Novo Conceito"), 
            QCoreApplication.translate("App", 
                                        "Digite o conceito:\n"
                                        "Ex: 'Tensão de Cisalhamento', 'Momento Fletor'"
                                        )
        )

        if ok and texto:
            if self.nos:
                ultimo = self.nos[-1]
                x = ultimo.scenePos().x() + 150
                y = ultimo.scenePos().y()

            else:
                x, y = 0, 0

            no = NoConceito(x, y, texto)
            if isinstance(self.scene, MapaScene):
                pos = self.scene.snap(QPointF(x, y))
                no.setPos(pos)

            self.scene.addItem(no)
            self.nos.append(no)
            self._expandir_area_se_necessario(no)

            if hasattr(self.view, "animate_focus_on"):
                self.view.animate_focus_on(no)

    except Exception as e:
        logger.error(f"Erro ao adicionar nó: {str(e)}", exc_info=True)
