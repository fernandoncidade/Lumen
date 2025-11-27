from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import QCursor
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()


class PDFMouseHandler(QObject):
    def __init__(self, pdf_view, owner=None):
        super().__init__(pdf_view)
        self.pdf_view = pdf_view
        self.owner = owner
        self.mode = None
        self.is_dragging = False
        self.drag_start_pos = None

        viewport = self.pdf_view.viewport()
        if viewport:
            viewport.installEventFilter(self)
            logger.debug("PDFMouseHandler inicializado (modo inativo)")

    def set_mode(self, mode):
        viewport = self.pdf_view.viewport()
        if not viewport:
            return

        if mode == "hand":
            self.mode = "hand"
            self.is_dragging = False
            self.drag_start_pos = None
            viewport.setCursor(QCursor(Qt.OpenHandCursor))
            logger.debug("Modo mão ativado - cursor OpenHand")

        else:
            self.mode = None
            self.is_dragging = False
            self.drag_start_pos = None
            viewport.setCursor(QCursor(Qt.ArrowCursor))
            logger.debug("Modo padrão ativado - cursor Arrow")

    def eventFilter(self, obj, event):
        try:
            viewport = self.pdf_view.viewport() if self.pdf_view else None
            if not viewport or obj != viewport:
                return super().eventFilter(obj, event)

            event_type = event.type()

            if event_type == QEvent.MouseButtonPress:
                return self._handle_mouse_press(event)

            elif event_type == QEvent.MouseMove:
                return self._handle_mouse_move(event)

            elif event_type == QEvent.MouseButtonRelease:
                return self._handle_mouse_release(event)

            elif event_type == QEvent.Wheel:
                return self._handle_wheel(event)

        except RuntimeError:
            return False

        except Exception as e:
            logger.error(f"Erro em eventFilter: {e}", exc_info=True)

        return super().eventFilter(obj, event)

    def _handle_mouse_press(self, event):
        try:
            if self.mode == "hand" and event.button() == Qt.LeftButton:
                self.is_dragging = True
                self.drag_start_pos = event.pos()

                viewport = self.pdf_view.viewport()
                if viewport:
                    viewport.setCursor(QCursor(Qt.ClosedHandCursor))

                logger.debug("Drag iniciado (modo mão)")
                return True

        except Exception as e:
            logger.error(f"Erro em mouse press: {e}", exc_info=True)

        return False

    def _handle_mouse_move(self, event):
        try:
            if self.mode == "hand" and self.is_dragging and self.drag_start_pos:
                delta = event.pos() - self.drag_start_pos

                h_scroll = self.pdf_view.horizontalScrollBar()
                v_scroll = self.pdf_view.verticalScrollBar()

                if h_scroll:
                    new_h = h_scroll.value() - delta.x()
                    h_scroll.setValue(new_h)

                if v_scroll:
                    new_v = v_scroll.value() - delta.y()
                    v_scroll.setValue(new_v)

                self.drag_start_pos = event.pos()

                return True

        except Exception as e:
            logger.error(f"Erro em mouse move: {e}", exc_info=True)

        return False

    def _handle_mouse_release(self, event):
        try:
            if self.mode == "hand" and event.button() == Qt.LeftButton:
                self.is_dragging = False
                self.drag_start_pos = None

                viewport = self.pdf_view.viewport()
                if viewport:
                    viewport.setCursor(QCursor(Qt.OpenHandCursor))

                logger.debug("Drag finalizado (modo mão)")
                return True

        except Exception as e:
            logger.error(f"Erro em mouse release: {e}", exc_info=True)

        return False

    def _handle_wheel(self, event):
        try:
            mode = None
            try:
                mode = getattr(self.owner, "_pdf_scroll_mode", None) if self.owner else None

            except Exception as e:
                logger.debug(f"Erro ao obter modo de rolagem do PDF: {e}", exc_info=True)
                mode = None

            if mode == "page":
                delta = 0
                try:
                    delta = event.angleDelta().y()

                except Exception as e:
                    logger.debug(f"Erro ao obter delta do evento roda do mouse: {e}", exc_info=True)
                    try:
                        delta = event.delta()

                    except Exception as e:
                        logger.debug(f"Erro ao obter delta do evento roda do mouse (fallback): {e}", exc_info=True)
                        delta = 0

                if delta > 0:
                    try:
                        if self.owner and hasattr(self.owner, "_pdf_prev_page"):
                            self.owner._pdf_prev_page()
                            try:
                                event.accept()

                            except Exception as e:
                                logger.debug(f"Erro ao aceitar evento roda do mouse: {e}", exc_info=True)

                            return True

                    except Exception as e:
                        logger.debug(f"Erro ao navegar para página anterior via roda: {e}", exc_info=True)

                elif delta < 0:
                    try:
                        if self.owner and hasattr(self.owner, "_pdf_next_page"):
                            self.owner._pdf_next_page()
                            try:
                                event.accept()

                            except Exception as e:
                                logger.debug(f"Erro ao aceitar evento roda do mouse: {e}", exc_info=True)

                            return True

                    except Exception as e:
                        logger.debug(f"Erro ao navegar para próxima página via roda: {e}", exc_info=True)

                return False

            return False

        except Exception as e:
            logger.error(f"Erro ao processar evento roda do mouse no PDF: {e}", exc_info=True)

        return False
