from __future__ import annotations
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QApplication
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


@dataclass
class CharInfo:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    page_index: int
    char_index: int

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2


class PDFTextSelection(QObject):
    selection_changed = Signal(str)

    def __init__(self, pdf_view, parent=None):
        super().__init__(parent)
        self.pdf_view = pdf_view
        self._chars_by_page: Dict[int, List[CharInfo]] = {}
        self._selection_start: Optional[Tuple[int, int]] = None
        self._selection_end: Optional[Tuple[int, int]] = None
        self._selected_chars: List[CharInfo] = []
        self._is_selecting: bool = False
        self._last_extracted_path: Optional[str] = None

    def clear_cache(self):
        self._chars_by_page.clear()
        self._last_extracted_path = None

    def clear_selection(self):
        self._selection_start = None
        self._selection_end = None
        self._selected_chars = []
        self._is_selecting = False
        self.selection_changed.emit("")

    def _extract_chars_for_page(self, page_index: int) -> List[CharInfo]:
        if page_index in self._chars_by_page:
            return self._chars_by_page[page_index]

        chars: List[CharInfo] = []

        try:
            plumber_doc = getattr(self.pdf_view, "_plumber_doc", None)
            if not plumber_doc:
                logger.debug("pdfplumber não disponível para extração de caracteres")
                return chars

            if page_index >= len(plumber_doc.pages):
                return chars

            page = plumber_doc.pages[page_index]
            page_chars = page.chars or []

            for idx, c in enumerate(page_chars):
                text = c.get("text", "")
                if not text:
                    continue

                char_info = CharInfo(
                    text=text,
                    x0=float(c.get("x0", 0)),
                    y0=float(c.get("top", 0)),
                    x1=float(c.get("x1", 0)),
                    y1=float(c.get("bottom", 0)),
                    page_index=page_index,
                    char_index=idx
                )
                chars.append(char_info)

            self._chars_by_page[page_index] = chars
            logger.debug(f"Extraídos {len(chars)} caracteres da página {page_index}")

        except Exception as e:
            logger.error(f"Erro ao extrair caracteres da página {page_index}: {e}", exc_info=True)

        return chars

    def get_char_at_position(self, page_index: int, x: float, y: float) -> Optional[CharInfo]:
        chars = self._extract_chars_for_page(page_index)
        if not chars:
            return None

        tolerance = 2.0

        for char in chars:
            if (char.x0 - tolerance <= x <= char.x1 + tolerance and
                char.y0 - tolerance <= y <= char.y1 + tolerance):
                return char

        return None

    def get_nearest_char(self, page_index: int, x: float, y: float) -> Optional[CharInfo]:
        chars = self._extract_chars_for_page(page_index)
        if not chars:
            return None

        y_tolerance = 10.0
        same_line_chars = [c for c in chars if abs(c.center_y - y) <= y_tolerance]

        if same_line_chars:
            nearest = min(same_line_chars, key=lambda c: abs(c.center_x - x))
            return nearest

        if chars:
            nearest = min(chars, key=lambda c: 
                ((c.center_x - x) ** 2 + (c.center_y - y) ** 2) ** 0.5
            )
            return nearest

        return None

    def get_insertion_point(self, page_index: int, x: float, y: float) -> Tuple[Optional[CharInfo], bool]:
        char = self.get_nearest_char(page_index, x, y)
        if not char:
            return (None, True)

        is_before = x < char.center_x
        return (char, is_before)

    def start_selection(self, page_index: int, x: float, y: float):
        self.clear_selection()
        self._is_selecting = True

        char = self.get_char_at_position(page_index, x, y)
        if char:
            self._selection_start = (page_index, char.char_index)
            self._selection_end = (page_index, char.char_index)
            self._update_selected_chars()

    def update_selection(self, page_index: int, x: float, y: float):
        if not self._is_selecting or self._selection_start is None:
            return

        char = self.get_char_at_position(page_index, x, y)
        if not char:
            char = self.get_nearest_char(page_index, x, y)

        if char:
            self._selection_end = (page_index, char.char_index)
            self._update_selected_chars()

    def end_selection(self):
        self._is_selecting = False
        if self._selected_chars:
            text = self.get_selected_text()
            self.selection_changed.emit(text)
            logger.debug(f"Seleção finalizada: {len(self._selected_chars)} caracteres")

    def _update_selected_chars(self):
        self._selected_chars = []

        if self._selection_start is None or self._selection_end is None:
            return

        start_page, start_idx = self._selection_start
        end_page, end_idx = self._selection_end

        if start_page > end_page or (start_page == end_page and start_idx > end_idx):
            start_page, end_page = end_page, start_page
            start_idx, end_idx = end_idx, start_idx

        for page_idx in range(start_page, end_page + 1):
            chars = self._extract_chars_for_page(page_idx)

            for char in chars:
                if page_idx == start_page == end_page:
                    if start_idx <= char.char_index <= end_idx:
                        self._selected_chars.append(char)

                elif page_idx == start_page:
                    if char.char_index >= start_idx:
                        self._selected_chars.append(char)

                elif page_idx == end_page:
                    if char.char_index <= end_idx:
                        self._selected_chars.append(char)

                else:
                    self._selected_chars.append(char)

    def get_selected_text(self) -> str:
        if not self._selected_chars:
            return ""

        sorted_chars = sorted(self._selected_chars, 
                              key=lambda c: (c.page_index, c.y0, c.x0))

        text_parts = []
        last_y = None
        last_page = None
        y_tolerance = 5.0

        for char in sorted_chars:
            if last_page is not None:
                if char.page_index != last_page:
                    text_parts.append("\n\n")

                elif last_y is not None and abs(char.y0 - last_y) > y_tolerance:
                    text_parts.append("\n")

            text_parts.append(char.text)
            last_y = char.y0
            last_page = char.page_index

        return "".join(text_parts)

    def copy_selection_to_clipboard(self):
        text = self.get_selected_text()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            logger.debug(f"Texto copiado para clipboard: {len(text)} caracteres")
            return True

        return False

    def get_selected_chars(self) -> List[CharInfo]:
        return self._selected_chars.copy()

    def has_selection(self) -> bool:
        return len(self._selected_chars) > 0

    def is_selecting(self) -> bool:
        return self._is_selecting

    def select_word_at(self, page_index: int, x: float, y: float) -> bool:
        char = self.get_char_at_position(page_index, x, y)
        if not char:
            return False

        chars = self._extract_chars_for_page(page_index)
        if not chars:
            return False

        word_chars = []
        char_idx = char.char_index

        y_tolerance = 5.0
        line_chars = [c for c in chars if abs(c.center_y - char.center_y) <= y_tolerance]
        line_chars.sort(key=lambda c: c.x0)

        current_line_idx = None
        for i, c in enumerate(line_chars):
            if c.char_index == char_idx:
                current_line_idx = i
                break

        if current_line_idx is None:
            return False

        start_idx = current_line_idx
        for i in range(current_line_idx - 1, -1, -1):
            c = line_chars[i]
            if not c.text.strip() or not (c.text.isalnum() or c.text in "-_'"):
                break

            start_idx = i

        end_idx = current_line_idx
        for i in range(current_line_idx + 1, len(line_chars)):
            c = line_chars[i]
            if not c.text.strip() or not (c.text.isalnum() or c.text in "-_'"):
                break

            end_idx = i

        if start_idx <= end_idx:
            self._selection_start = (page_index, line_chars[start_idx].char_index)
            self._selection_end = (page_index, line_chars[end_idx].char_index)
            self._update_selected_chars()
            self._is_selecting = False
            if self._selected_chars:
                self.selection_changed.emit(self.get_selected_text())
                return True

        return False

    def select_line_at(self, page_index: int, x: float, y: float) -> bool:
        char = self.get_nearest_char(page_index, x, y)
        if not char:
            return False

        chars = self._extract_chars_for_page(page_index)
        if not chars:
            return False

        y_tolerance = 5.0
        line_chars = [c for c in chars if abs(c.center_y - char.center_y) <= y_tolerance]

        if not line_chars:
            return False

        line_chars.sort(key=lambda c: c.x0)

        self._selection_start = (page_index, line_chars[0].char_index)
        self._selection_end = (page_index, line_chars[-1].char_index)
        self._update_selected_chars()
        self._is_selecting = False

        if self._selected_chars:
            self.selection_changed.emit(self.get_selected_text())
            return True

        return False

def get_selection_color() -> QColor:
    return QColor(0, 120, 215, 100)

def paint_selection(painter: QPainter, chars: List[CharInfo], zoom: float, offset_x: int, offset_y: int):
    if not chars:
        return

    color = get_selection_color()
    painter.save()
    painter.setBrush(color)
    painter.setPen(Qt.NoPen)

    y_tolerance = 3.0
    lines: List[List[CharInfo]] = []
    current_line: List[CharInfo] = []
    last_y = None

    sorted_chars = sorted(chars, key=lambda c: (c.y0, c.x0))

    for char in sorted_chars:
        if last_y is None or abs(char.y0 - last_y) <= y_tolerance:
            current_line.append(char)

        else:
            if current_line:
                lines.append(current_line)

            current_line = [char]

        last_y = char.y0

    if current_line:
        lines.append(current_line)

    for line in lines:
        if not line:
            continue

        line.sort(key=lambda c: c.x0)

        x0 = min(c.x0 for c in line)
        y0 = min(c.y0 for c in line)
        x1 = max(c.x1 for c in line)
        y1 = max(c.y1 for c in line)

        rect_x = offset_x + int(x0 * zoom)
        rect_y = offset_y + int(y0 * zoom)
        rect_w = int((x1 - x0) * zoom)
        rect_h = int((y1 - y0) * zoom)

        painter.fillRect(rect_x, rect_y, rect_w, rect_h, color)

    painter.restore()
