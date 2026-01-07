from __future__ import annotations
import uuid
import weakref
from PySide6.QtCore import QPoint, Qt, Signal, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QTabBar, QTabWidget, QApplication


_LUMEN_TAB_MIME = "application/x-lumen-module-tab"
_DRAG_REGISTRY: dict[str, dict] = {}


class _DetachableTabBar(QTabBar):
    detach_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setAcceptDrops(True)
        self._drag_start: QPoint | None = None
        self._drag_index: int | None = None
        self._detaching = False

    def _start_reattach_drag(self) -> None:
        win = self.window()
        if not getattr(win, "detached", False):
            return

        module_id = getattr(win, "detached_module_id", None)
        title = getattr(win, "detached_title", None)
        widget = getattr(win, "detached_widget", None)
        origin_index = getattr(win, "detached_origin_index", None)
        if not module_id or widget is None:
            return

        token = uuid.uuid4().hex
        _DRAG_REGISTRY[token] = {
            "module_id": module_id,
            "title": title or "",
            "widget": widget,
            "origin_index": origin_index,
            "detached_window": weakref.ref(win),
        }

        mime = QMimeData()
        mime.setData(_LUMEN_TAB_MIME, token.encode("utf-8"))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.MoveAction)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            self._drag_start = pos
            self._drag_index = self.tabAt(pos)
            self._detaching = False

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._detaching or self._drag_start is None or self._drag_index is None:
            return super().mouseMoveEvent(event)

        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        if (pos - self._drag_start).manhattanLength() < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        global_pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
        local_pos = self.mapFromGlobal(global_pos)

        if not self.rect().contains(local_pos):
            idx = self._drag_index
            self._detaching = True
            self._drag_start = None
            self._drag_index = None
            if 0 <= idx < self.count():
                event.accept()

                if getattr(self.window(), "detached", False):
                    self._start_reattach_drag()
                    return

                self.detach_requested.emit(idx)
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_start = None
        self._drag_index = None
        self._detaching = False
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        try:
            if event.mimeData().hasFormat(_LUMEN_TAB_MIME):
                event.acceptProposedAction()
                return

        except Exception:
            pass

        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        try:
            if event.mimeData().hasFormat(_LUMEN_TAB_MIME):
                event.acceptProposedAction()
                return

        except Exception:
            pass

        super().dragMoveEvent(event)

    def dropEvent(self, event):
        try:
            if not event.mimeData().hasFormat(_LUMEN_TAB_MIME):
                return super().dropEvent(event)

            token = bytes(event.mimeData().data(_LUMEN_TAB_MIME)).decode("utf-8", errors="ignore")
            payload = _DRAG_REGISTRY.pop(token, None)
            if not payload:
                return

            host = self.window()
            if getattr(host, "detached", False):
                return

            det_ref = payload.get("detached_window")
            detached_win = det_ref() if callable(det_ref) else None

            module_id = payload.get("module_id")
            title = payload.get("title")
            widget = payload.get("widget")
            origin_index = payload.get("origin_index")

            if widget is None or not module_id:
                return

            try:
                if detached_win is not None and hasattr(detached_win, "tabs"):
                    idx = detached_win.tabs.indexOf(widget)
                    if idx >= 0:
                        detached_win.tabs.removeTab(idx)

            except Exception:
                pass

            try:
                widget.setParent(None)

            except Exception:
                pass

            try:
                host._reattach_module_tab(module_id, widget, title, origin_index=origin_index)

            except Exception:
                try:
                    host._reattach_module_tab(module_id, widget, title)

                except Exception:
                    pass

            try:
                if detached_win is not None:
                    detached_win.detached_reattached = True
                    detached_win.close()

            except Exception:
                pass

            event.setDropAction(Qt.MoveAction)
            event.accept()
            return

        finally:
            try:
                super().dropEvent(event)

            except Exception:
                pass


class DetachableTabWidget(QTabWidget):
    detach_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        bar = _DetachableTabBar(self)
        bar.detach_requested.connect(self.detach_requested.emit)
        self.setTabBar(bar)
