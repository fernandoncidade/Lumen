from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from PySide6.QtCore import Qt, QRect, QRectF, QSize, QTimer, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QSizePolicy
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

if TYPE_CHECKING:
    import fitz as _fitz
    FitDocument = _fitz.Document
    FitPixmap = _fitz.Pixmap
    FitRect = _fitz.Rect

else:
    FitDocument = Any
    FitPixmap = Any
    FitRect = Any

try:
    import fitz

except Exception as e:
    fitz = None
    logger.error(f"PyMuPDF (fitz) não disponível: {e}", exc_info=True)


@dataclass
class PageHit:
    page_index: int
    rect: FitRect

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def _qimage_from_fitz_pixmap(pm: FitPixmap) -> QImage:
    fmt = QImage.Format_RGBA8888 if pm.alpha else QImage.Format_RGB888
    img = QImage(pm.samples, pm.width, pm.height, pm.stride, fmt)
    return img.copy()

def _fitz_flag(*names: str) -> int:
    try:
        if not fitz:
            return 0

        for n in names:
            if hasattr(fitz, n):
                try:
                    return int(getattr(fitz, n))

                except Exception:
                    continue

    except Exception:
        pass

    return 0

def _norm_ws(s: str) -> str:
    return " ".join((s or "").split())


class MuPDFPageWidget(QWidget):
    def __init__(self, owner_view: "MuPDFView", page_index: int):
        super().__init__()
        self._owner = owner_view
        self.page_index = page_index
        self._pixmap: Optional[QPixmap] = None
        self._pixmap_zoom: Optional[float] = None

        self._highlights: List[FitRect] = []
        self._current_hit_idx: Optional[int] = None

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_highlights(self, rects: List[FitRect], current_idx: Optional[int]):
        self._highlights = rects or []
        self._current_hit_idx = current_idx
        self.update()

    def clear_render(self):
        self._pixmap = None
        self._pixmap_zoom = None
        self.updateGeometry()
        self.update()

    def ensure_rendered(self):
        try:
            if not self._owner or not self._owner._doc:
                return
            z = float(self._owner._zoom)
            if self._pixmap is not None and self._pixmap_zoom is not None and abs(self._pixmap_zoom - z) < 1e-6:
                return

            pm = self._owner.render_page_pixmap(self.page_index, z)
            if pm is None:
                return

            img = _qimage_from_fitz_pixmap(pm)
            self._pixmap = QPixmap.fromImage(img)
            self._pixmap_zoom = z
            self.updateGeometry()
            self.update()

        except Exception as e:
            logger.error(f"Falha ao renderizar página {self.page_index}: {e}", exc_info=True)

    def sizeHint(self) -> QSize:
        if self._pixmap:
            return QSize(self._pixmap.width(), self._pixmap.height() + 16)

        return QSize(800, 1000)

    def minimumSizeHint(self) -> QSize:
        return QSize(200, 200)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        p.fillRect(self.rect(), self.palette().color(self.backgroundRole()))

        if not self._pixmap:
            p.setPen(QColor(120, 120, 120))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"Página {self.page_index + 1}")
            return

        x = max(0, int((self.width() - self._pixmap.width()) / 2))
        y = 0
        p.drawPixmap(x, y, self._pixmap)

        if fitz and self._highlights:
            z = float(self._owner._zoom)
            brush_all = QColor(255, 235, 59, 110)
            brush_cur = QColor(255, 152, 0, 140)
            pen_cur = QColor(255, 87, 34, 200)

            for idx, r in enumerate(self._highlights):
                try:
                    rr = QRectF(
                        x + (r.x0 * z),
                        y + (r.y0 * z),
                        (r.x1 - r.x0) * z,
                        (r.y1 - r.y0) * z,
                    )

                    if self._current_hit_idx is not None and idx == self._current_hit_idx:
                        p.fillRect(rr, brush_cur)
                        p.setPen(pen_cur)
                        p.drawRect(rr)

                    else:
                        p.fillRect(rr, brush_all)

                except Exception:
                    continue

        p.setPen(QColor(0, 0, 0, 25))
        p.drawLine(0, self._pixmap.height() + 8, self.width(), self._pixmap.height() + 8)
        p.end()


class MuPDFView(QScrollArea):
    search_results_changed = Signal(int)
    current_page_changed = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self._doc: Optional[FitDocument] = None
        self._path: Optional[str] = None

        self._zoom: float = 1.0
        self._scroll_mode: str = "continuous"
        self._current_page: int = 0

        self._pix_cache: Dict[Tuple[int, int], FitPixmap] = {}
        self._pix_cache_order: List[Tuple[int, int]] = []
        self._pix_cache_max = 16

        self._hits: List[PageHit] = []
        self._hits_by_page: Dict[int, List[FitRect]] = {}
        self._hit_cursor: int = -1
        self._highlight_all: bool = True

        self._container = QWidget()
        self._vbox = QVBoxLayout(self._container)
        self._vbox.setContentsMargins(16, 16, 16, 16)
        self._vbox.setSpacing(8)
        self.setWidget(self._container)

        self._page_widgets: List[MuPDFPageWidget] = []

        self.verticalScrollBar().valueChanged.connect(lambda _: self._schedule_render_visible())
        self.verticalScrollBar().valueChanged.connect(lambda _: self._schedule_update_current_page())

        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._render_visible_pages_now)

        self._page_timer = QTimer(self)
        self._page_timer.setSingleShot(True)
        self._page_timer.timeout.connect(self._update_current_page_now)

    def pageCount(self) -> int:
        try:
            return int(self._doc.page_count) if self._doc else 0

        except Exception:
            return 0

    def zoomFactor(self) -> float:
        return float(self._zoom)

    def setZoomFactor(self, z: float):
        z = float(_clamp(z, 0.25, 5.0))
        if abs(self._zoom - z) < 1e-6:
            return

        self._zoom = z
        self._invalidate_all_pages()
        self._schedule_render_visible()

    def currentPage(self) -> int:
        return int(self._current_page)

    def load_pdf(self, path: str) -> bool:
        if not fitz:
            logger.error("PyMuPDF não está disponível (fitz import falhou).")
            return False

        try:
            self.clear()
            self._doc = fitz.open(path)
            self._path = path
            self._current_page = 0
            self._zoom = 1.0

            self._build_pages()
            self._schedule_render_visible()

            self.current_page_changed.emit(0, self.pageCount())
            return True

        except Exception as e:
            logger.error(f"Falha ao abrir PDF via PyMuPDF: {path} :: {e}", exc_info=True)
            self.clear()
            return False

    def clear(self):
        try:
            self._doc = None
            self._path = None
            self._hits = []
            self._hits_by_page = {}
            self._hit_cursor = -1
            self._pix_cache.clear()
            self._pix_cache_order.clear()

            for w in list(self._page_widgets):
                w.setParent(None)

            self._page_widgets = []

        except Exception:
            pass

    def _build_pages(self):
        for w in list(self._page_widgets):
            w.setParent(None)

        self._page_widgets = []

        if not self._doc:
            return

        total = self.pageCount()
        for i in range(total):
            pw = MuPDFPageWidget(self, i)
            self._vbox.addWidget(pw)
            self._page_widgets.append(pw)

        self._vbox.addStretch(1)

    def _zoom_key(self, z: float) -> int:
        return int(round(z * 1000))

    def render_page_pixmap(self, page_index: int, zoom: float) -> Optional[FitPixmap]:
        try:
            if not self._doc:
                return None

            zk = self._zoom_key(zoom)
            key = (int(page_index), int(zk))
            if key in self._pix_cache:
                return self._pix_cache[key]

            page = self._doc.load_page(page_index)
            mat = fitz.Matrix(zoom, zoom)
            pm = page.get_pixmap(matrix=mat, alpha=False)

            self._pix_cache[key] = pm
            self._pix_cache_order.append(key)
            while len(self._pix_cache_order) > self._pix_cache_max:
                old = self._pix_cache_order.pop(0)
                try:
                    self._pix_cache.pop(old, None)

                except Exception:
                    pass

            return pm

        except Exception as e:
            logger.debug(f"Falha render_page_pixmap({page_index}): {e}", exc_info=True)
            return None

    def _invalidate_all_pages(self):
        try:
            self._pix_cache.clear()
            self._pix_cache_order.clear()
            for w in self._page_widgets:
                w.clear_render()

            self._apply_highlights_to_widgets()

        except Exception:
            pass

    def _schedule_render_visible(self):
        try:
            if not self._render_timer.isActive():
                self._render_timer.start(40)
        except Exception:
            pass

    def _schedule_update_current_page(self):
        try:
            if not self._page_timer.isActive():
                self._page_timer.start(40)

        except Exception:
            pass

    def _render_visible_pages_now(self):
        try:
            if not self._page_widgets:
                return

            vp = self.viewport()
            vr = QRect(0, self.verticalScrollBar().value(), vp.width(), vp.height())

            extra = 600
            top = vr.top() - extra
            bottom = vr.bottom() + extra

            for w in self._page_widgets:
                geo = w.geometry()
                if geo.bottom() < top:
                    continue

                if geo.top() > bottom:
                    continue

                w.ensure_rendered()

            self._apply_highlights_to_widgets()

        except Exception as e:
            logger.debug(f"Falha ao renderizar páginas visíveis: {e}", exc_info=True)

    def _update_current_page_now(self):
        try:
            if not self._page_widgets:
                return

            total = self.pageCount()
            if total <= 0:
                return

            mid_y = self.verticalScrollBar().value() + int(self.viewport().height() / 2)

            chosen = None
            for i, w in enumerate(self._page_widgets):
                g = w.geometry()
                if g.top() <= mid_y <= g.bottom():
                    chosen = i
                    break

            if chosen is None:
                chosen = 0 if mid_y < self._page_widgets[0].geometry().top() else (len(self._page_widgets) - 1)

            if chosen != self._current_page:
                self._current_page = int(chosen)
                self.current_page_changed.emit(self._current_page, total)

        except Exception:
            pass

    def goto_page(self, page_index: int):
        try:
            total = self.pageCount()
            if total <= 0:
                return

            page_index = int(_clamp(page_index, 0, total - 1))
            self._current_page = page_index

            if 0 <= page_index < len(self._page_widgets):
                w = self._page_widgets[page_index]
                self.ensureWidgetVisible(w, 0, 0)

            self.current_page_changed.emit(self._current_page, total)

            self._schedule_render_visible()

        except Exception as e:
            logger.debug(f"Falha goto_page({page_index}): {e}", exc_info=True)

    def next_page(self):
        self.goto_page(self._current_page + 1)

    def prev_page(self):
        self.goto_page(self._current_page - 1)

    def fit_width(self):
        try:
            if not self._doc or not self._page_widgets:
                return

            page0 = self._doc.load_page(0)
            rect = page0.rect  # em pontos
            vpw = max(100, self.viewport().width() - 48)
            z = vpw / max(1.0, float(rect.width))
            self.setZoomFactor(_clamp(z, 0.25, 5.0))

        except Exception as e:
            logger.debug(f"Falha fit_width: {e}", exc_info=True)

    def fit_page(self):
        try:
            if not self._doc:
                return

            page0 = self._doc.load_page(0)
            rect = page0.rect
            vpw = max(100, self.viewport().width() - 48)
            vph = max(100, self.viewport().height() - 48)
            z_w = vpw / max(1.0, float(rect.width))
            z_h = vph / max(1.0, float(rect.height))
            self.setZoomFactor(_clamp(min(z_w, z_h), 0.25, 5.0))

        except Exception as e:
            logger.debug(f"Falha fit_page: {e}", exc_info=True)

    def set_highlight_all(self, enable: bool):
        self._highlight_all = bool(enable)
        self._apply_highlights_to_widgets()

    def clear_search(self):
        self._hits = []
        self._hits_by_page = {}
        self._hit_cursor = -1
        self._apply_highlights_to_widgets()
        self.search_results_changed.emit(0)

    def search(self, query: str, match_case: bool = False, whole_words: bool = False) -> int:
        try:
            if not self._doc:
                self.clear_search()
                return 0

            q = (query or "").strip()
            if not q:
                self.clear_search()
                return 0

            hits: List[PageHit] = []
            hits_by_page: Dict[int, List[FitRect]] = {}

            IGNORECASE = _fitz_flag("TEXT_IGNORECASE", "TEXT_SEARCH_IGNORECASE", "TEXTFLAGS_IGNORECASE")
            MATCHCASE = _fitz_flag("TEXT_MATCHCASE", "TEXT_SEARCH_MATCHCASE", "TEXT_SEARCH_CASESENSITIVE", "TEXT_CASESENSITIVE")

            flags = 0
            if match_case:
                if MATCHCASE:
                    flags |= MATCHCASE

            else:
                if IGNORECASE:
                    flags |= IGNORECASE

            is_simple = (" " not in q) and ("\n" not in q) and ("\t" not in q)
            qn = _norm_ws(q)

            for i in range(self.pageCount()):
                page = self._doc.load_page(i)

                rects: List[FitRect] = []
                if whole_words and is_simple:
                    words = page.get_text("words") or []
                    for w in words:
                        txt = str(w[4] or "")
                        if match_case:
                            ok = (txt == q)

                        else:
                            ok = (txt.lower() == q.lower())

                        if ok:
                            rects.append(fitz.Rect(w[0], w[1], w[2], w[3]))

                else:
                    rects = page.search_for(q, flags=flags) or []
                    if match_case and rects:
                        filtered: List[FitRect] = []
                        for r in rects:
                            try:
                                clip_txt = _norm_ws(page.get_text("text", clip=r) or "")
                                if qn and (qn in clip_txt):
                                    filtered.append(r)

                            except Exception:
                                filtered.append(r)

                        rects = filtered

                if rects:
                    hits_by_page[i] = rects
                    for r in rects:
                        hits.append(PageHit(page_index=i, rect=r))

            self._hits = hits
            self._hits_by_page = hits_by_page
            self._hit_cursor = 0 if hits else -1

            self._apply_highlights_to_widgets()
            self.search_results_changed.emit(len(hits))
            if hits:
                self._scroll_to_current_hit()

            return len(hits)

        except Exception as e:
            logger.error(f"Falha search('{query}'): {e}", exc_info=True)
            self.clear_search()
            return 0

    def current_hit_position(self) -> Tuple[int, int]:
        total = len(self._hits)
        if total <= 0 or self._hit_cursor < 0:
            return (0, 0)

        return (self._hit_cursor + 1, total)

    def goto_next_hit(self):
        if not self._hits:
            return

        self._hit_cursor = (self._hit_cursor + 1) % len(self._hits)
        self._apply_highlights_to_widgets()
        self._scroll_to_current_hit()

    def goto_prev_hit(self):
        if not self._hits:
            return

        self._hit_cursor = (self._hit_cursor - 1) % len(self._hits)
        self._apply_highlights_to_widgets()
        self._scroll_to_current_hit()

    def _scroll_to_current_hit(self):
        try:
            if not self._hits or self._hit_cursor < 0:
                return

            cur = self._hits[self._hit_cursor]
            self.goto_page(cur.page_index)

            z = float(self._zoom)
            y = int(cur.rect.y0 * z)
            target = max(0, self._page_widgets[cur.page_index].y() + y - int(self.viewport().height() * 0.25))
            self.verticalScrollBar().setValue(target)

        except Exception:
            pass

    def _apply_highlights_to_widgets(self):
        try:
            if not fitz:
                return

            if not self._page_widgets:
                return

            current_page = None
            current_rect = None
            if self._hits and self._hit_cursor >= 0:
                cur = self._hits[self._hit_cursor]
                current_page = cur.page_index
                current_rect = cur.rect

            for i, w in enumerate(self._page_widgets):
                rects = self._hits_by_page.get(i, [])
                if not self._highlight_all and current_page is not None:
                    rects_to_use = rects if i == current_page else []

                else:
                    rects_to_use = rects

                cur_idx = None
                if current_page == i and current_rect is not None and rects_to_use:
                    try:
                        for idx, rr in enumerate(rects_to_use):
                            if abs(rr.x0 - current_rect.x0) < 0.5 and abs(rr.y0 - current_rect.y0) < 0.5:
                                cur_idx = idx
                                break

                    except Exception:
                        cur_idx = None

                w.set_highlights(rects_to_use, cur_idx)

        except Exception:
            pass
