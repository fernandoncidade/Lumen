from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QPalette
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def atualizar_tema(self):
    try:
        app = QCoreApplication.instance()
        pal = app.palette() if app else self.palette()

        bg_brush = pal.brush(QPalette.Base)

        self.scene.setBackgroundBrush(bg_brush)
        self.view.setBackgroundBrush(bg_brush)

        vp = self.view.viewport()
        vp.setPalette(pal)
        vp.setAutoFillBackground(True)

        for w in (self.view, vp):
            st = w.style()
            try:
                st.unpolish(w)
                st.polish(w)

            except Exception:
                pass

            w.update()

        for sb in (self.view.horizontalScrollBar(), self.view.verticalScrollBar()):
            if not sb:
                continue

            sb.setPalette(pal)

            if sb.styleSheet():
                sb.setStyleSheet("")

            st = sb.style()

            try:
                st.unpolish(sb)
                st.polish(sb)

            except Exception:
                pass

            sb.update()

    except Exception as e:
        logger.error(f"Erro ao aplicar tema dinâmico: {str(e)}", exc_info=True)
