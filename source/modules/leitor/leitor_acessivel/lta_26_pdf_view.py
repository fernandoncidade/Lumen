from __future__ import annotations
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from PySide6.QtCore import Qt, QRect, QRectF, QSize, QTimer, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QSizePolicy
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

pypdfium2_available = False
pdf2image_available = False
pdfplumber_available = False
PIL_available = False

try:
    import pypdfium2 as pdfium
    pypdfium2_available = True
    logger.debug("pypdfium2 disponível - usando como backend de renderização PDF")

except ImportError as e:
    logger.debug(f"pypdfium2 não disponível: {e}")
    pdfium = None

if not pypdfium2_available:
    try:
        from pdf2image import convert_from_path
        from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError
        pdf2image_available = True
        logger.debug("pdf2image disponível - usando como backend de renderização PDF")

    except ImportError as e:
        logger.warning(f"pdf2image não disponível: {e}")
        convert_from_path = None
        PDFInfoNotInstalledError = Exception
        PDFPageCountError = Exception

else:
    convert_from_path = None
    PDFInfoNotInstalledError = Exception
    PDFPageCountError = Exception

try:
    import pdfplumber
    pdfplumber_available = True

except ImportError as e:
    logger.warning(f"pdfplumber não disponível: {e}")
    pdfplumber = None

try:
    from PIL import Image
    PIL_available = True

except ImportError as e:
    logger.warning(f"PIL não disponível: {e}")
    Image = None

def _get_poppler_path() -> Optional[str]:
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        poppler_path = os.path.join(base_path, 'poppler')
        if os.path.exists(poppler_path):
            return poppler_path

    return None


@dataclass
class PageHit:
    page_index: int
    rect: Tuple[float, float, float, float]
    text: str = ""


@dataclass
class SimpleRect:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def _pil_to_qimage(pil_image) -> QImage:
    if pil_image is None:
        return QImage()

    try:
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")

        data = pil_image.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)
        return qimg.copy()

    except Exception as e:
        logger.error(f"Erro ao converter PIL para QImage: {e}", exc_info=True)
        return QImage()

def _norm_ws(s: str) -> str:
    return " ".join((s or "").split())


class PDFPageWidget(QWidget):
    def __init__(self, owner_view: "PDFView", page_index: int):
        super().__init__()
        self._owner = owner_view
        self.page_index = page_index
        self._pixmap: Optional[QPixmap] = None
        self._pixmap_zoom: Optional[float] = None

        self._highlights: List[SimpleRect] = []
        self._current_hit_idx: Optional[int] = None

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_highlights(self, rects: List[SimpleRect], current_idx: Optional[int]):
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
            if not self._owner or not self._owner._pdf_path:
                return

            z = float(self._owner._zoom)
            if self._pixmap is not None and self._pixmap_zoom is not None and abs(self._pixmap_zoom - z) < 1e-6:
                return

            pil_img = self._owner.render_page_pil(self.page_index, z)
            if pil_img is None:
                return

            qimg = _pil_to_qimage(pil_img)
            if qimg.isNull():
                return

            self._pixmap = QPixmap.fromImage(qimg)
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

        if self._highlights:
            z = float(self._owner._zoom)
            brush_all = QColor(255, 235, 59, 110)
            brush_cur = QColor(255, 152, 0, 140)
            pen_cur = QColor(255, 87, 34, 200)

            for idx, r in enumerate(self._highlights):
                try:
                    rr = QRectF(
                        x + (r.x0 * z),
                        y + (r.y0 * z),
                        r.width * z,
                        r.height * z,
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


class PDFView(QScrollArea):
    search_results_changed = Signal(int)
    current_page_changed = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self._pdf_path: Optional[str] = None
        self._page_count: int = 0
        self._page_sizes: List[Tuple[float, float]] = []

        self._zoom: float = 1.0
        self._scroll_mode: str = "continuous"
        self._current_page: int = 0

        self._pdfium_doc = None

        self._pix_cache: Dict[Tuple[int, int], Any] = {}
        self._pix_cache_order: List[Tuple[int, int]] = []
        self._pix_cache_max = 16

        self._hits: List[PageHit] = []
        self._hits_by_page: Dict[int, List[SimpleRect]] = {}
        self._hit_cursor: int = -1
        self._highlight_all: bool = True

        self._container = QWidget()
        self._vbox = QVBoxLayout(self._container)
        self._vbox.setContentsMargins(16, 16, 16, 16)
        self._vbox.setSpacing(8)
        self.setWidget(self._container)

        self._page_widgets: List[PDFPageWidget] = []

        self.verticalScrollBar().valueChanged.connect(lambda _: self._schedule_render_visible())
        self.verticalScrollBar().valueChanged.connect(lambda _: self._schedule_update_current_page())

        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._render_visible_pages_now)

        self._page_timer = QTimer(self)
        self._page_timer.setSingleShot(True)
        self._page_timer.timeout.connect(self._update_current_page_now)

        self._plumber_doc = None

    @staticmethod
    def is_available() -> bool:
        return (pypdfium2_available or pdf2image_available) and PIL_available

    def pageCount(self) -> int:
        return self._page_count

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
        if not pypdfium2_available and not pdf2image_available:
            logger.error("Nenhum backend de renderização PDF disponível (pypdfium2 ou pdf2image).")
            return False

        try:
            self.clear()

            if pypdfium2_available:
                try:
                    self._pdfium_doc = pdfium.PdfDocument(path)
                    self._page_count = len(self._pdfium_doc)

                    self._page_sizes = []
                    for i in range(self._page_count):
                        page = self._pdfium_doc[i]
                        w, h = page.get_size()
                        self._page_sizes.append((float(w), float(h)))

                    logger.debug(f"PDF carregado via pypdfium2: {self._page_count} páginas")

                except Exception as e:
                    logger.warning(f"Erro ao usar pypdfium2: {e}")
                    self._pdfium_doc = None

            if pdfplumber_available:
                try:
                    self._plumber_doc = pdfplumber.open(path)

                    if self._page_count == 0:
                        self._page_count = len(self._plumber_doc.pages)
                        self._page_sizes = []
                        for page in self._plumber_doc.pages:
                            w = float(page.width)
                            h = float(page.height)
                            self._page_sizes.append((w, h))

                except Exception as e:
                    logger.warning(f"Erro ao usar pdfplumber: {e}")
                    self._plumber_doc = None

            if self._page_count == 0 and pdf2image_available:
                try:
                    from pdf2image import pdfinfo_from_path
                    info = pdfinfo_from_path(path, poppler_path=_get_poppler_path())
                    self._page_count = info.get("Pages", 0)

                except Exception as e:
                    logger.warning(f"Erro ao obter info via pdf2image: {e}")
                    try:
                        images = convert_from_path(
                            path, dpi=72, first_page=1, last_page=1,
                            poppler_path=_get_poppler_path()
                        )
                        if images:
                            self._page_count = 1
                            try:
                                all_images = convert_from_path(
                                    path, dpi=36,
                                    poppler_path=_get_poppler_path()
                                )
                                self._page_count = len(all_images)

                            except Exception:
                                pass

                    except Exception as e2:
                        logger.error(f"Falha ao obter contagem de páginas: {e2}")
                        return False

            if self._page_count == 0:
                logger.error("PDF não contém páginas ou não pôde ser lido.")
                return False

            self._pdf_path = path
            self._current_page = 0
            self._zoom = 1.0

            self._build_pages()
            self._schedule_render_visible()

            self.current_page_changed.emit(0, self.pageCount())
            return True

        except Exception as e:
            logger.error(f"Falha ao abrir PDF: {path} :: {e}", exc_info=True)
            self.clear()
            return False

    def clear(self):
        try:
            if self._pdfium_doc:
                try:
                    self._pdfium_doc.close()

                except Exception:
                    pass

                self._pdfium_doc = None

            if self._plumber_doc:
                try:
                    self._plumber_doc.close()

                except Exception:
                    pass

                self._plumber_doc = None

            self._pdf_path = None
            self._page_count = 0
            self._page_sizes = []
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

        if not self._pdf_path or self._page_count == 0:
            return

        for i in range(self._page_count):
            pw = PDFPageWidget(self, i)
            self._vbox.addWidget(pw)
            self._page_widgets.append(pw)

        self._vbox.addStretch(1)

    def _zoom_key(self, z: float) -> int:
        return int(round(z * 1000))

    def render_page_pil(self, page_index: int, zoom: float) -> Optional[Any]:
        try:
            if not self._pdf_path:
                return None

            zk = self._zoom_key(zoom)
            key = (int(page_index), int(zk))
            if key in self._pix_cache:
                return self._pix_cache[key]

            pil_img = None

            if pypdfium2_available and self._pdfium_doc:
                try:
                    page = self._pdfium_doc[page_index]
                    scale = zoom
                    bitmap = page.render(scale=scale)
                    pil_img = bitmap.to_pil()

                except Exception as e:
                    logger.debug(f"Falha ao renderizar via pypdfium2: {e}")
                    pil_img = None

            if pil_img is None and pdf2image_available:
                try:
                    dpi = int(72 * zoom)
                    dpi = max(36, min(300, dpi))

                    images = convert_from_path(
                        self._pdf_path,
                        dpi=dpi,
                        first_page=page_index + 1,
                        last_page=page_index + 1,
                        fmt="png",
                        poppler_path=_get_poppler_path()
                    )

                    if images:
                        pil_img = images[0]

                except Exception as e:
                    logger.debug(f"Falha ao renderizar via pdf2image: {e}")
                    pil_img = None

            if pil_img is None:
                return None

            self._pix_cache[key] = pil_img
            self._pix_cache_order.append(key)
            while len(self._pix_cache_order) > self._pix_cache_max:
                old = self._pix_cache_order.pop(0)
                try:
                    self._pix_cache.pop(old, None)

                except Exception:
                    pass

            return pil_img

        except Exception as e:
            logger.debug(f"Falha render_page_pil({page_index}): {e}", exc_info=True)
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
            if not self._pdf_path or not self._page_sizes:
                return

            page_width = self._page_sizes[0][0] if self._page_sizes else 612
            vpw = max(100, self.viewport().width() - 48)
            z = vpw / max(1.0, float(page_width))
            self.setZoomFactor(_clamp(z, 0.25, 5.0))

        except Exception as e:
            logger.debug(f"Falha fit_width: {e}", exc_info=True)

    def fit_page(self):
        try:
            if not self._pdf_path or not self._page_sizes:
                return

            page_width, page_height = self._page_sizes[0] if self._page_sizes else (612, 792)
            vpw = max(100, self.viewport().width() - 48)
            vph = max(100, self.viewport().height() - 48)
            z_w = vpw / max(1.0, float(page_width))
            z_h = vph / max(1.0, float(page_height))
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

    def _find_text_spans(self, page, query: str, match_case: bool, whole_words: bool) -> List[SimpleRect]:
        results: List[SimpleRect] = []

        try:
            chars = page.chars or []
            words = page.extract_words(
                x_tolerance=3,
                y_tolerance=3,
                keep_blank_chars=False,
                use_text_flow=True,
                extra_attrs=["fontname", "size"]
            ) or []

            if not chars and not words:
                return results

            q = query if match_case else query.lower()

            if chars and len(q) <= 50:
                results = self._search_in_chars(chars, q, match_case, whole_words)
                if results:
                    return results

            if words:
                results = self._search_in_words(words, q, match_case, whole_words)

            return results

        except Exception as e:
            logger.debug(f"Erro em _find_text_spans: {e}", exc_info=True)
            return results

    def _search_in_chars(self, chars: List[Dict], query: str, match_case: bool, whole_words: bool) -> List[SimpleRect]:
        results: List[SimpleRect] = []

        if not chars:
            return results

        try:
            page_text = ""
            char_positions = []

            for c in chars:
                txt = c.get("text", "")
                if txt:
                    char_positions.append((c, len(page_text)))
                    page_text += txt

            if not page_text:
                return results

            search_text = page_text if match_case else page_text.lower()
            search_query = query if match_case else query.lower()

            start = 0
            while True:
                idx = search_text.find(search_query, start)
                if idx == -1:
                    break

                if whole_words:
                    if idx > 0 and search_text[idx - 1].isalnum():
                        start = idx + 1
                        continue

                    end_idx = idx + len(search_query)
                    if end_idx < len(search_text) and search_text[end_idx].isalnum():
                        start = idx + 1
                        continue

                match_chars = []
                for c, pos in char_positions:
                    if pos >= idx and pos < idx + len(search_query):
                        match_chars.append(c)

                if match_chars:
                    x0 = min(float(c.get("x0", 0)) for c in match_chars)
                    y0 = min(float(c.get("top", 0)) for c in match_chars)
                    x1 = max(float(c.get("x1", 0)) for c in match_chars)
                    y1 = max(float(c.get("bottom", 0)) for c in match_chars)

                    results.append(SimpleRect(x0=x0, y0=y0, x1=x1, y1=y1))

                start = idx + 1

        except Exception as e:
            logger.debug(f"Erro em _search_in_chars: {e}", exc_info=True)

        return results

    def _search_in_words(self, words: List[Dict], query: str, match_case: bool, whole_words: bool) -> List[SimpleRect]:
        results: List[SimpleRect] = []

        if not words:
            return results

        try:
            lines: List[List[Dict]] = []
            current_line: List[Dict] = []
            last_top = None
            y_tolerance = 5

            sorted_words = sorted(words, key=lambda w: (float(w.get("top", 0)), float(w.get("x0", 0))))

            for w in sorted_words:
                top = float(w.get("top", 0))
                if last_top is None or abs(top - last_top) <= y_tolerance:
                    current_line.append(w)

                else:
                    if current_line:
                        lines.append(current_line)

                    current_line = [w]

                last_top = top

            if current_line:
                lines.append(current_line)

            for line in lines:
                line_results = self._search_in_line(line, query, match_case, whole_words)
                results.extend(line_results)

            if len(lines) > 1 and " " in query:
                cross_line_results = self._search_across_lines(lines, query, match_case, whole_words)
                for r in cross_line_results:
                    is_dup = any(
                        abs(r.x0 - existing.x0) < 1 and abs(r.y0 - existing.y0) < 1
                        for existing in results
                    )

                    if not is_dup:
                        results.append(r)

        except Exception as e:
            logger.debug(f"Erro em _search_in_words: {e}", exc_info=True)

        return results

    def _search_in_line(self, line_words: List[Dict], query: str, match_case: bool, whole_words: bool) -> List[SimpleRect]:
        results: List[SimpleRect] = []

        if not line_words:
            return results

        try:
            line_text = ""
            word_spans = []

            for w in line_words:
                txt = w.get("text", "")
                if txt:
                    start = len(line_text)
                    line_text += txt
                    word_spans.append((w, start, len(line_text)))
                    line_text += " "

            line_text = line_text.rstrip()

            if not line_text:
                return results

            search_text = line_text if match_case else line_text.lower()
            search_query = query if match_case else query.lower()

            start = 0
            while True:
                idx = search_text.find(search_query, start)
                if idx == -1:
                    break

                end_idx = idx + len(search_query)

                if whole_words:
                    if idx > 0 and search_text[idx - 1].isalnum():
                        start = idx + 1
                        continue

                    if end_idx < len(search_text) and search_text[end_idx].isalnum():
                        start = idx + 1
                        continue

                matching_words = []
                for w, ws, we in word_spans:
                    if ws < end_idx and we > idx:
                        matching_words.append(w)

                if matching_words:
                    x0 = min(float(w.get("x0", 0)) for w in matching_words)
                    y0 = min(float(w.get("top", 0)) for w in matching_words)
                    x1 = max(float(w.get("x1", 0)) for w in matching_words)
                    y1 = max(float(w.get("bottom", 0)) for w in matching_words)

                    results.append(SimpleRect(x0=x0, y0=y0, x1=x1, y1=y1))

                start = idx + 1

        except Exception as e:
            logger.debug(f"Erro em _search_in_line: {e}", exc_info=True)

        return results

    def _search_across_lines(self, lines: List[List[Dict]], query: str, match_case: bool, whole_words: bool) -> List[SimpleRect]:
        results: List[SimpleRect] = []

        try:
            for i in range(len(lines) - 1):
                current_line = lines[i]
                next_line = lines[i + 1]

                if not current_line or not next_line:
                    continue

                n_words = min(5, len(query.split()))
                tail_words = current_line[-n_words:] if len(current_line) >= n_words else current_line
                head_words = next_line[:n_words] if len(next_line) >= n_words else next_line

                tail_text = " ".join(w.get("text", "") for w in tail_words)
                head_text = " ".join(w.get("text", "") for w in head_words)
                combined = tail_text + " " + head_text

                search_text = combined if match_case else combined.lower()
                search_query = query if match_case else query.lower()

                tail_len = len(tail_text)
                idx = search_text.find(search_query)

                if idx != -1 and idx < tail_len and idx + len(search_query) > tail_len:
                    if whole_words:
                        if idx > 0 and search_text[idx - 1].isalnum():
                            continue

                        end_idx = idx + len(search_query)
                        if end_idx < len(search_text) and search_text[end_idx].isalnum():
                            continue

                    matching_words = []

                    char_count = 0
                    for w in tail_words:
                        w_text = w.get("text", "")
                        w_start = char_count
                        w_end = char_count + len(w_text)

                        if w_start < tail_len and w_end > idx:
                            matching_words.append(w)

                        char_count = w_end + 1

                    query_in_next = idx + len(search_query) - tail_len - 1
                    char_count = 0
                    for w in head_words:
                        w_text = w.get("text", "")
                        w_end = char_count + len(w_text)

                        if char_count < query_in_next:
                            matching_words.append(w)

                        char_count = w_end + 1

                    if matching_words:
                        x0 = min(float(w.get("x0", 0)) for w in matching_words)
                        y0 = min(float(w.get("top", 0)) for w in matching_words)
                        x1 = max(float(w.get("x1", 0)) for w in matching_words)
                        y1 = max(float(w.get("bottom", 0)) for w in matching_words)

                        results.append(SimpleRect(x0=x0, y0=y0, x1=x1, y1=y1))

        except Exception as e:
            logger.debug(f"Erro em _search_across_lines: {e}", exc_info=True)

        return results

    def search(self, query: str, match_case: bool = False, whole_words: bool = False) -> int:
        try:
            if not pdfplumber_available or not self._plumber_doc:
                logger.warning("pdfplumber não disponível para busca.")
                self.clear_search()
                return 0

            q = (query or "").strip()
            if not q:
                self.clear_search()
                return 0

            hits: List[PageHit] = []
            hits_by_page: Dict[int, List[SimpleRect]] = {}

            for page_idx, page in enumerate(self._plumber_doc.pages):
                try:
                    page_rects = self._find_text_spans(page, q, match_case, whole_words)

                    for rect in page_rects:
                        hits.append(PageHit(
                            page_index=page_idx,
                            rect=(rect.x0, rect.y0, rect.x1, rect.y1),
                            text=q
                        ))

                    if page_rects:
                        hits_by_page[page_idx] = page_rects

                except Exception as e:
                    logger.debug(f"Erro ao buscar na página {page_idx}: {e}")
                    continue

            self._hits = hits
            self._hits_by_page = hits_by_page
            self._hit_cursor = 0 if hits else -1

            self._apply_highlights_to_widgets()
            self.search_results_changed.emit(len(hits))

            if hits:
                self._scroll_to_current_hit()

            logger.debug(f"Busca '{q}': {len(hits)} resultados encontrados")
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
            y = int(cur.rect[1] * z)  # y0
            target = max(0, self._page_widgets[cur.page_index].y() + y - int(self.viewport().height() * 0.25))
            self.verticalScrollBar().setValue(target)

        except Exception:
            pass

    def _apply_highlights_to_widgets(self):
        try:
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
                            if abs(rr.x0 - current_rect[0]) < 0.5 and abs(rr.y0 - current_rect[1]) < 0.5:
                                cur_idx = idx
                                break

                    except Exception:
                        cur_idx = None

                w.set_highlights(rects_to_use, cur_idx)

        except Exception:
            pass
