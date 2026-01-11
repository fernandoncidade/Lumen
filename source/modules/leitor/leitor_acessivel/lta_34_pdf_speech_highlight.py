from PySide6.QtCore import QObject, QTimer, Signal
from source.utils.LogManager import LogManager
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from bisect import bisect_left
logger = LogManager.get_logger()


class PDFHighlightMode(Enum):
    WORD = "word"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"


@dataclass
class PDFHighlightStyle:
    background_color: str = "#FF9800"
    border_color: str = "#FF5722"
    opacity: int = 180


@dataclass
class PDFWordRect:
    page_index: int
    x0: float
    y0: float
    x1: float
    y1: float
    text: str = ""


class PDFSpeechHighlightManager(QObject):
    word_highlighted = Signal(int, object)
    highlight_cleared = Signal()
    position_changed = Signal(int)

    def __init__(self, pdf_view, parent: QObject = None):
        super().__init__(parent)
        self._pdf_view = pdf_view
        self._timestamps: List[Dict] = []
        self._word_positions: List[PDFWordRect] = []
        self._current_index = -1
        self._is_active = False
        self._is_paused = False
        self._base_position_ms = 0
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_highlight)
        self._update_interval = 50
        self._mode = PDFHighlightMode.WORD
        self._style = PDFHighlightStyle()
        self._auto_scroll = True
        self._enabled = True
        self._force_reapply = False
        self._media_player = None
        self._chunk_base_offset = 0
        self._next_chunk_base_offset = 0
        self._current_chunk_index = 0
        self._extracted_text = ""
        self._text_to_pdf_mapping: List[Tuple[int, PDFWordRect]] = []
        self._mapping_offsets: List[int] = []
        self._mapping_rects: List[PDFWordRect] = []

        logger.debug("PDFSpeechHighlightManager inicializado")

    def set_media_player(self, player):
        self._media_player = player
        logger.debug("Media player configurado no PDFSpeechHighlightManager")

    def set_timestamps(self, timestamps: List[Dict], append: bool = False):
        if append:
            if self._timestamps:
                last_ts = self._timestamps[-1]
                base_offset = last_ts["offset_ms"] + last_ts["duration_ms"]
                self._next_chunk_base_offset = base_offset
                for ts in timestamps:
                    ts["offset_ms"] += base_offset

            self._timestamps.extend(timestamps)

        else:
            self._timestamps = list(timestamps)
            self._chunk_base_offset = 0
            self._next_chunk_base_offset = 0

        logger.debug(f"[PDF] Timestamps configurados: {len(self._timestamps)} palavras, chunk_base: {self._chunk_base_offset}")

    def set_word_positions(self, positions: List[PDFWordRect]):
        self._word_positions = positions
        logger.debug(f"[PDF] Posições de palavras configuradas: {len(positions)} palavras")

    def set_text_to_pdf_mapping(self, mapping: List[Tuple[int, PDFWordRect]]):
        self._text_to_pdf_mapping = list(mapping or [])

        try:
            self._text_to_pdf_mapping.sort(key=lambda x: int(x[0]))

        except Exception:
            pass

        self._mapping_offsets = [int(off) for off, _ in self._text_to_pdf_mapping]
        self._mapping_rects = [rect for _, rect in self._text_to_pdf_mapping]

        logger.debug(f"[PDF] Mapeamento texto->PDF configurado: {len(self._text_to_pdf_mapping)} entradas")

    def set_extracted_text(self, text: str):
        self._extracted_text = text

    def set_mode(self, mode: PDFHighlightMode):
        old_mode = self._mode
        self._mode = mode
        logger.debug(f"[PDF] Modo de highlight alterado para: {mode.value}")

        if old_mode != mode:
            self._clear_highlight()
            self._force_reapply = True
            if self._is_active and not self._is_paused and self._current_index >= 0:
                self._apply_highlight_at_index(self._current_index)

    def set_style(self, style: PDFHighlightStyle):
        self._style = style

    def set_auto_scroll(self, enabled: bool):
        self._auto_scroll = enabled

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if not enabled:
            self.stop()

    def is_enabled(self) -> bool:
        return self._enabled

    def start(self, start_position_ms: int = 0):
        if not self._enabled:
            logger.debug("[PDF] PDFSpeechHighlightManager está desabilitado")
            return

        if not self._timestamps:
            logger.debug("[PDF] Sem timestamps para sincronizar")
            return

        self._is_active = True
        self._is_paused = False
        self._base_position_ms = start_position_ms
        self._current_index = -1

        self._update_timer.start(self._update_interval)
        logger.debug(f"[PDF] Realce sincronizado iniciado em {start_position_ms}ms com {len(self._timestamps)} timestamps")

    def pause(self):
        if self._is_active:
            self._is_paused = True
            self._update_timer.stop()
            logger.debug("[PDF] Realce sincronizado pausado")

    def resume(self):
        if self._is_active and self._is_paused:
            self._is_paused = False
            self._update_timer.start(self._update_interval)
            logger.debug("[PDF] Realce sincronizado retomado")

    def stop(self):
        self._update_timer.stop()
        self._is_active = False
        self._is_paused = False
        self._current_index = -1
        self._clear_highlight()
        self.highlight_cleared.emit()
        logger.debug("[PDF] Realce sincronizado parado")

    def clear_timestamps(self):
        self._timestamps = []
        self._current_index = -1
        self._chunk_base_offset = 0
        self._next_chunk_base_offset = 0
        self._current_chunk_index = 0

    def _norm_token(self, s: str) -> str:
        try:
            return "".join(ch for ch in (s or "").strip().lower() if ch.isalnum())

        except Exception:
            return (s or "").strip().lower()

    def notify_new_chunk_started(self, chunk_index: int = None, base_offset_ms: int = None):
        if chunk_index is not None:
            self._current_chunk_index = chunk_index

        else:
            self._current_chunk_index += 1

        if base_offset_ms is not None:
            self._chunk_base_offset = base_offset_ms

        else:
            self._chunk_base_offset = self._next_chunk_base_offset

        logger.debug(f"[PDF] Novo chunk iniciado: índice={self._current_chunk_index}, base_offset={self._chunk_base_offset}ms")

    def _get_current_position_ms(self) -> int:
        if self._media_player is None:
            return 0

        try:
            player_pos = self._media_player.position()
            return player_pos + self._chunk_base_offset

        except Exception:
            return 0

    def _find_timestamp_at_position(self, position_ms: int) -> int:
        for i, ts in enumerate(self._timestamps):
            offset = ts.get("offset_ms", 0)
            duration = ts.get("duration_ms", 0)

            if offset <= position_ms < offset + duration:
                return i

            if offset > position_ms:
                return max(0, i - 1)

        if self._timestamps:
            return len(self._timestamps) - 1

        return -1

    def _update_highlight(self):
        if not self._is_active or self._is_paused or not self._timestamps:
            return

        current_ms = self._get_current_position_ms()
        self.position_changed.emit(current_ms)
        new_index = self._find_timestamp_at_position(current_ms)
        should_apply = (new_index != self._current_index and new_index >= 0) or self._force_reapply

        if should_apply and new_index >= 0:
            self._current_index = new_index
            self._force_reapply = False
            self._apply_highlight_at_index(new_index)

    def _apply_highlight_at_index(self, index: int):
        if index < 0 or index >= len(self._timestamps):
            return

        try:
            ts = self._timestamps[index]
            text_offset = ts.get("text_offset", 0)
            word_text = ts.get("text", "")
            word_rect = self._find_rect_for_offset(text_offset, word_text)

            if word_rect is not None:
                if self._mode == PDFHighlightMode.WORD:
                    self._apply_highlight_rect(word_rect)

                elif self._mode == PDFHighlightMode.SENTENCE:
                    rects = self._get_sentence_rects(text_offset)
                    self._apply_highlight_rects(rects)

                else:
                    rects = self._get_paragraph_rects(text_offset)
                    self._apply_highlight_rects(rects)

                self.word_highlighted.emit(index, word_rect)

                if self._auto_scroll:
                    self._scroll_to_rect(word_rect)

            else:
                logger.debug(f"[PDF] Não encontrou retângulo para offset {text_offset}, palavra '{word_text}'")

        except Exception as e:
            logger.debug(f"[PDF] Erro ao aplicar highlight no índice {index}: {e}", exc_info=True)

    def _find_rect_for_offset(self, text_offset: int, word_text: str) -> Optional[PDFWordRect]:
        try:
            if self._mapping_offsets and self._mapping_rects:
                target = int(text_offset)
                i = bisect_left(self._mapping_offsets, target)

                best_idx = None
                best_dist = 10**9
                start = max(0, i - 4)
                end = min(len(self._mapping_offsets), i + 5)
                for j in range(start, end):
                    d = abs(self._mapping_offsets[j] - target)
                    if d < best_dist:
                        best_dist = d
                        best_idx = j

                    if d == 0:
                        return self._mapping_rects[j]

                want = self._norm_token(word_text)
                if want:
                    j0 = max(0, i - 60)
                    j1 = min(len(self._mapping_rects), i + 61)
                    cand_idx = None
                    cand_dist = 10**9
                    for j in range(j0, j1):
                        have = self._norm_token(getattr(self._mapping_rects[j], "text", ""))
                        if have == want:
                            d = abs(self._mapping_offsets[j] - target)
                            if d < cand_dist:
                                cand_dist = d
                                cand_idx = j
                                if d == 0:
                                    break

                    if cand_idx is not None:
                        return self._mapping_rects[cand_idx]

                if best_idx is not None and best_dist <= 120:
                    return self._mapping_rects[best_idx]

            return None

        except Exception as e:
            logger.debug(f"[PDF] Erro ao buscar retângulo: {e}")
            return None

    def _get_sentence_rects(self, text_offset: int) -> List[PDFWordRect]:
        rects = []
        try:
            if not self._text_to_pdf_mapping:
                logger.debug("[PDF] _get_sentence_rects: mapeamento vazio")
                return rects

            text = self._extracted_text
            if not text:
                logger.debug("[PDF] _get_sentence_rects: texto extraído vazio")
                return rects

            text_offset = max(0, min(text_offset, len(text) - 1))

            start = text_offset
            while start > 0:
                char = text[start - 1]
                if char in '.!?\n':
                    break

                start -= 1

            end = text_offset
            while end < len(text):
                char = text[end]
                if char in '.!?\n':
                    end += 1
                    break

                end += 1

            logger.debug(f"[PDF] _get_sentence_rects: buscando rects entre offset {start} e {end}")

            for offset, rect in self._text_to_pdf_mapping:
                if start <= offset < end:
                    rects.append(rect)

            logger.debug(f"[PDF] _get_sentence_rects: encontrados {len(rects)} retângulos")

        except Exception as e:
            logger.debug(f"[PDF] Erro ao obter rects da frase: {e}", exc_info=True)

        return rects

    def _get_paragraph_rects(self, text_offset: int) -> List[PDFWordRect]:
        rects = []
        try:
            if not self._text_to_pdf_mapping:
                logger.debug("[PDF] _get_paragraph_rects: mapeamento vazio")
                return rects

            text = self._extracted_text
            if not text:
                logger.debug("[PDF] _get_paragraph_rects: texto extraído vazio")
                return rects

            text_offset = max(0, min(text_offset, len(text) - 1))

            start = text_offset
            while start > 0:
                if text[start - 1] == '\n':
                    break

                start -= 1

            end = text_offset
            while end < len(text):
                if text[end] == '\n':
                    break

                end += 1

            logger.debug(f"[PDF] _get_paragraph_rects: buscando rects entre offset {start} e {end}")

            for offset, rect in self._text_to_pdf_mapping:
                if start <= offset < end:
                    rects.append(rect)

            logger.debug(f"[PDF] _get_paragraph_rects: encontrados {len(rects)} retângulos")

        except Exception as e:
            logger.debug(f"[PDF] Erro ao obter rects do parágrafo: {e}", exc_info=True)

        return rects

    def _apply_highlight_rect(self, rect: PDFWordRect):
        try:
            if self._pdf_view is None:
                return

            from .lta_26_pdf_view import SimpleRect
            simple_rect = SimpleRect(
                x0=rect.x0,
                y0=rect.y0,
                x1=rect.x1,
                y1=rect.y1
            )

            self._pdf_view.set_speech_highlight(rect.page_index, simple_rect)

        except Exception as e:
            logger.debug(f"[PDF] Erro ao aplicar highlight rect: {e}", exc_info=True)

    def _apply_highlight_rects(self, rects: List[PDFWordRect]):
        try:
            if self._pdf_view is None:
                return

            if not rects:
                self._pdf_view.clear_speech_highlight()
                return

            from .lta_26_pdf_view import SimpleRect

            by_page: Dict[int, List[SimpleRect]] = {}
            for rect in rects:
                if rect.page_index not in by_page:
                    by_page[rect.page_index] = []

                by_page[rect.page_index].append(SimpleRect(
                    x0=rect.x0,
                    y0=rect.y0,
                    x1=rect.x1,
                    y1=rect.y1
                ))

            self._pdf_view.set_speech_highlights(by_page)

        except Exception as e:
            logger.debug(f"[PDF] Erro ao aplicar highlight rects: {e}", exc_info=True)

    def _clear_highlight(self):
        try:
            if self._pdf_view is not None:
                self._pdf_view.clear_speech_highlight()

        except Exception:
            pass

    def _scroll_to_rect(self, rect: PDFWordRect):
        try:
            if self._pdf_view is None:
                return

            self._pdf_view.scroll_to_highlight(rect.page_index, rect.y0)

        except Exception:
            pass

def extract_word_positions_from_pdf(pdf_path: str, page_index: Optional[int] = None) -> Tuple[str, List[PDFWordRect], List[Tuple[int, PDFWordRect]]]:
    word_rects: List[PDFWordRect] = []
    mapping: List[Tuple[int, PDFWordRect]] = []
    text_builder = []
    current_offset = 0

    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            pages = list(enumerate(pdf.pages))
            if page_index is not None:
                try:
                    pi = int(page_index)
                    if 0 <= pi < len(pdf.pages):
                        pages = [(pi, pdf.pages[pi])]
                    else:
                        pages = []
                except Exception:
                    pages = []

            for page_idx, page in pages:
                try:
                    words = page.extract_words(
                        x_tolerance=3,
                        y_tolerance=3,
                        keep_blank_chars=False,
                        use_text_flow=True
                    ) or []

                    if page_index is None and page_idx > 0 and text_builder:
                        text_builder.append("\n\n")
                        current_offset += 2

                    last_bottom = None

                    for word in words:
                        word_text = word.get("text", "")
                        if not word_text:
                            continue

                        word_top = float(word.get("top", 0))

                        if last_bottom is not None:
                            if word_top - last_bottom > 5:
                                if text_builder and text_builder[-1] not in ['\n', ' ']:
                                    if word_top - last_bottom > 15:
                                        text_builder.append("\n")
                                        current_offset += 1

                                    text_builder.append(" ")
                                    current_offset += 1

                            elif text_builder and text_builder[-1] not in ['\n', ' ']:
                                text_builder.append(" ")
                                current_offset += 1

                        rect = PDFWordRect(
                            page_index=page_idx,
                            x0=float(word.get("x0", 0)),
                            y0=word_top,
                            x1=float(word.get("x1", 0)),
                            y1=float(word.get("bottom", 0)),
                            text=word_text
                        )

                        word_rects.append(rect)
                        mapping.append((current_offset, rect))
                        text_builder.append(word_text)
                        current_offset += len(word_text)
                        last_bottom = float(word.get("bottom", 0))

                except Exception as e:
                    logger.debug(f"[PDF] Erro ao extrair palavras da página {page_idx}: {e}")
                    continue

    except Exception as e:
        logger.error(f"[PDF] Erro ao extrair posições de palavras: {e}", exc_info=True)

    full_text = "".join(text_builder)
    logger.debug(f"[PDF] Extraídas {len(word_rects)} palavras, {len(full_text)} caracteres")
    return full_text, word_rects, mapping
