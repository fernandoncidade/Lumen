from PySide6.QtCore import Qt, QObject, QEvent, QTimer
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

        self._text_selection = None
        self._click_count = 0
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._reset_click_count)
        self._last_click_pos = None

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
            self._clear_text_selection()
            logger.debug("Modo mão ativado - cursor OpenHand")

        elif mode == "select":
            self.mode = "select"
            self.is_dragging = False
            self.drag_start_pos = None
            viewport.setCursor(QCursor(Qt.IBeamCursor))
            try:
                if viewport.focusPolicy() == Qt.FocusPolicy.NoFocus:
                    viewport.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

                viewport.setFocus(Qt.FocusReason.MouseFocusReason)

            except Exception:
                pass

            self._ensure_text_selection()
            self._update_page_widgets()
            logger.debug("Modo seleção ativado - cursor IBeam")

        else:
            self.mode = None
            self.is_dragging = False
            self.drag_start_pos = None
            viewport.setCursor(QCursor(Qt.ArrowCursor))
            logger.debug("Modo padrão ativado - cursor Arrow")

    def _ensure_text_selection(self):
        if self._text_selection is None:
            try:
                from .lta_31_pdf_text_selection import PDFTextSelection
                self._text_selection = PDFTextSelection(self.pdf_view, parent=self.pdf_view)
                self._text_selection.selection_changed.connect(self._on_selection_changed)
                logger.debug("PDFTextSelection criado")

            except Exception as e:
                logger.error(f"Erro ao criar PDFTextSelection: {e}", exc_info=True)

    def _clear_text_selection(self):
        if self._text_selection:
            self._text_selection.clear_selection()
            self._update_page_widgets()

    def _on_selection_changed(self, text: str):
        if text:
            logger.debug(f"Seleção alterada: {len(text)} caracteres")

        self._update_page_widgets()

    def _update_page_widgets(self):
        try:
            if self.pdf_view and hasattr(self.pdf_view, "_page_widgets"):
                selected_chars = []
                caret_by_page = {}
                if self._text_selection:
                    selected_chars = self._text_selection.get_selected_chars()
                    try:
                        caret_by_page = self._text_selection.get_caret_by_page() or {}

                    except Exception:
                        caret_by_page = {}

                for pw in self.pdf_view._page_widgets:
                    page_chars = [c for c in selected_chars if c.page_index == pw.page_index]
                    pw._selected_chars = page_chars
                    pw._caret = caret_by_page.get(pw.page_index)
                    pw.update()

        except Exception as e:
            logger.debug(f"Erro ao atualizar widgets: {e}")

    def _reset_click_count(self):
        self._click_count = 0

    def get_text_selection(self):
        return self._text_selection

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

            elif event_type == QEvent.MouseButtonDblClick:
                return self._handle_double_click(event)

        except RuntimeError:
            return False

        except Exception as e:
            logger.error(f"Erro em eventFilter: {e}", exc_info=True)

        return super().eventFilter(obj, event)

    def _viewport_to_pdf_coords(self, pos) -> tuple:
        try:
            if not self.pdf_view or not hasattr(self.pdf_view, "_page_widgets"):
                return (None, None, None)

            scroll_pos = pos

            for pw in self.pdf_view._page_widgets:
                try:
                    geo = pw.geometry()

                    widget_top = geo.top() - self.pdf_view.verticalScrollBar().value()
                    widget_bottom = geo.bottom() - self.pdf_view.verticalScrollBar().value()
                    widget_left = geo.left() - self.pdf_view.horizontalScrollBar().value()
                    widget_right = geo.right() - self.pdf_view.horizontalScrollBar().value()

                    if (widget_left <= scroll_pos.x() <= widget_right and
                        widget_top <= scroll_pos.y() <= widget_bottom):

                        rel_x = scroll_pos.x() - widget_left
                        rel_y = scroll_pos.y() - widget_top

                        pixmap = pw._pixmap
                        if pixmap:
                            pixmap_x_offset = max(0, (pw.width() - pixmap.width()) // 2)
                            rel_x -= pixmap_x_offset

                        zoom = float(self.pdf_view._zoom)
                        pdf_x = rel_x / zoom
                        pdf_y = rel_y / zoom

                        return (pw.page_index, pdf_x, pdf_y)

                except Exception as e:
                    logger.debug(f"Erro ao converter coords para página: {e}")
                    continue

            return (None, None, None)

        except Exception as e:
            logger.error(f"Erro em _viewport_to_pdf_coords: {e}", exc_info=True)
            return (None, None, None)

    def _handle_mouse_press(self, event):
        try:
            if event.button() == Qt.LeftButton:
                if self.mode == "hand":
                    self.is_dragging = True
                    self.drag_start_pos = event.pos()

                    viewport = self.pdf_view.viewport()
                    if viewport:
                        viewport.setCursor(QCursor(Qt.ClosedHandCursor))

                    logger.debug("Drag iniciado (modo mão)")
                    return True

                elif self.mode == "select":
                    self._ensure_text_selection()

                    if self._text_selection:
                        page_idx, pdf_x, pdf_y = self._viewport_to_pdf_coords(event.pos())

                        if page_idx is not None:
                            self._text_selection.set_caret_from_position(page_idx, pdf_x, pdf_y)
                            
                            current_pos = event.pos()

                            if (self._last_click_pos and
                                abs(current_pos.x() - self._last_click_pos.x()) < 5 and
                                abs(current_pos.y() - self._last_click_pos.y()) < 5 and
                                self._click_timer.isActive()):
                                self._click_count += 1

                            else:
                                self._click_count = 1

                            self._last_click_pos = current_pos
                            self._click_timer.start(400)

                            logger.debug(f"Mouse press - click_count={self._click_count}")

                            if self._click_count == 1:
                                self._text_selection.start_selection(page_idx, pdf_x, pdf_y)
                                self.is_dragging = True
                                self.drag_start_pos = event.pos()

                            elif self._click_count == 2:
                                self._text_selection.select_word_at(page_idx, pdf_x, pdf_y)
                                logger.debug("Duplo clique (via press) - selecionando palavra")

                            elif self._click_count >= 3:
                                self._text_selection.select_line_at(page_idx, pdf_x, pdf_y)
                                logger.debug("Triplo clique (via press) - selecionando linha")
                                self._click_count = 0

                            self._update_page_widgets()
                            return True

        except Exception as e:
            logger.error(f"Erro em mouse press: {e}", exc_info=True)

        return False

    def _handle_double_click(self, event):
        try:
            if self.mode == "select" and event.button() == Qt.LeftButton:
                self._ensure_text_selection()

                if self._text_selection:
                    page_idx, pdf_x, pdf_y = self._viewport_to_pdf_coords(event.pos())

                    if page_idx is not None:
                        try:
                            self._text_selection.set_caret_from_position(page_idx, pdf_x, pdf_y)

                        except Exception:
                            pass

                        current_pos = event.pos()

                        if (self._last_click_pos and
                            abs(current_pos.x() - self._last_click_pos.x()) < 5 and
                            abs(current_pos.y() - self._last_click_pos.y()) < 5 and
                            self._click_timer.isActive()):
                            self._click_count += 1

                        else:
                            self._click_count = 2

                        self._last_click_pos = current_pos
                        self._click_timer.start(400)

                        if self._click_count >= 3:
                            self._text_selection.select_line_at(page_idx, pdf_x, pdf_y)
                            self._click_count = 0
                            logger.debug("Triplo clique detectado - selecionando linha")

                        else:
                            self._text_selection.select_word_at(page_idx, pdf_x, pdf_y)
                            logger.debug("Duplo clique detectado - selecionando palavra")

                        self._update_page_widgets()
                        return True

        except Exception as e:
            logger.error(f"Erro em double click: {e}", exc_info=True)

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

            elif self.mode == "select" and self.is_dragging:
                if self._text_selection and self._text_selection.is_selecting():
                    page_idx, pdf_x, pdf_y = self._viewport_to_pdf_coords(event.pos())

                    if page_idx is not None:
                        self._text_selection.update_selection(page_idx, pdf_x, pdf_y)
                        self._update_page_widgets()
                        return True

        except Exception as e:
            logger.error(f"Erro em mouse move: {e}", exc_info=True)

        return False

    def _handle_mouse_release(self, event):
        try:
            if event.button() == Qt.LeftButton:
                if self.mode == "hand":
                    self.is_dragging = False
                    self.drag_start_pos = None

                    viewport = self.pdf_view.viewport()
                    if viewport:
                        viewport.setCursor(QCursor(Qt.OpenHandCursor))

                    logger.debug("Drag finalizado (modo mão)")
                    return True

                elif self.mode == "select":
                    if self._text_selection and self._text_selection.is_selecting():
                        self._text_selection.end_selection()
                        self._update_page_widgets()

                    self.is_dragging = False
                    self.drag_start_pos = None
                    return True

        except Exception as e:
            logger.error(f"Erro em mouse release: {e}", exc_info=True)

        return False

    def copy_selection(self) -> bool:
        if self._text_selection:
            return self._text_selection.copy_selection_to_clipboard()

        return False

    def get_selected_text(self) -> str:
        if self._text_selection:
            return self._text_selection.get_selected_text()

        return ""

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
