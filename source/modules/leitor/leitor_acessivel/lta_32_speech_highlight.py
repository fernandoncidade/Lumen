from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat
from PySide6.QtWidgets import QTextEdit
from source.utils.LogManager import LogManager
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
logger = LogManager.get_logger()


class HighlightMode(Enum):
    WORD = "word"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"


@dataclass
class HighlightStyle:
    background_color: str = "#FFEB3B"
    text_color: str = "#000000"
    current_word_bg: str = "#FF9800"
    current_word_fg: str = "#000000"
    underline: bool = False
    bold: bool = False


class SpeechHighlightManager(QObject):
    word_highlighted = Signal(int, int)
    highlight_cleared = Signal()
    position_changed = Signal(int)

    def __init__(self, text_edit: QTextEdit, parent: QObject = None):
        super().__init__(parent)
        self._text_edit = text_edit
        self._timestamps: List[Dict] = []
        self._current_index = -1
        self._is_active = False
        self._is_paused = False
        self._base_position_ms = 0
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_highlight)
        self._update_interval = 50
        self._mode = HighlightMode.WORD
        self._style = HighlightStyle()
        self._auto_scroll = True
        self._enabled = True
        self._force_reapply = False
        self._media_player = None
        self._previous_selections = []
        self._original_text = ""
        self._chunk_base_offset = 0
        self._next_chunk_base_offset = 0
        self._current_chunk_index = 0

        logger.debug("SpeechHighlightManager inicializado")

    def set_media_player(self, player):
        self._media_player = player
        logger.debug("Media player configurado no SpeechHighlightManager")

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

        logger.debug(f"Timestamps configurados: {len(self._timestamps)} palavras, chunk_base: {self._chunk_base_offset}")
    
    def set_original_text(self, text: str):
        self._original_text = text

    def set_mode(self, mode: HighlightMode):
        old_mode = self._mode
        self._mode = mode
        logger.debug(f"Modo de highlight alterado para: {mode.value}")

        if old_mode != mode:
            self._clear_highlight()
            self._force_reapply = True
            if self._is_active and not self._is_paused and self._current_index >= 0:
                self._apply_highlight_at_index(self._current_index)

    def set_style(self, style: HighlightStyle):
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
            logger.debug("SpeechHighlightManager está desabilitado")
            return

        if not self._timestamps:
            logger.debug("Sem timestamps para sincronizar")
            return

        self._is_active = True
        self._is_paused = False
        self._base_position_ms = start_position_ms
        self._current_index = -1

        try:
            self._previous_selections = self._text_edit.extraSelections()

        except Exception:
            self._previous_selections = []

        self._update_timer.start(self._update_interval)
        logger.debug(f"Realce sincronizado iniciado em {start_position_ms}ms com {len(self._timestamps)} timestamps")

    def pause(self):
        if self._is_active:
            self._is_paused = True
            self._update_timer.stop()
            logger.debug("Realce sincronizado pausado")

    def resume(self):
        if self._is_active and self._is_paused:
            self._is_paused = False
            self._update_timer.start(self._update_interval)
            logger.debug("Realce sincronizado retomado")

    def stop(self):
        self._update_timer.stop()
        self._is_active = False
        self._is_paused = False
        self._current_index = -1

        self._clear_highlight()

        try:
            if self._previous_selections:
                self._text_edit.setExtraSelections(self._previous_selections)

        except Exception:
            pass

        self.highlight_cleared.emit()
        logger.debug("Realce sincronizado parado")

    def clear_timestamps(self):
        self._timestamps = []
        self._current_index = -1
        self._chunk_base_offset = 0
        self._next_chunk_base_offset = 0
        self._current_chunk_index = 0

    def notify_new_chunk_started(self, chunk_index: int, base_offset_ms: int = None):
        self._current_chunk_index = chunk_index
        if base_offset_ms is not None:
            self._chunk_base_offset = base_offset_ms

        else:
            self._chunk_base_offset = self._next_chunk_base_offset

        logger.debug(f"Novo chunk iniciado: índice={chunk_index}, base_offset={self._chunk_base_offset}ms")

    def seek_to_position(self, position_ms: int):
        if not self._timestamps:
            return

        idx = self._find_timestamp_at_position(position_ms)
        if idx >= 0:
            self._current_index = idx
            self._apply_highlight_at_index(idx)

    def _get_current_position_ms(self) -> int:
        if self._media_player is None:
            return 0

        try:
            return self._media_player.position() + self._chunk_base_offset

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
            word_length = len(word_text)

            editor_text = self._text_edit.toPlainText()
            editor_text_len = len(editor_text)

            if editor_text_len == 0:
                logger.debug("Editor vazio, ignorando highlight")
                return

            if text_offset < 0:
                text_offset = 0

            if text_offset >= editor_text_len:
                word_lower = word_text.lower()
                found_pos = editor_text.lower().find(word_lower)
                if found_pos >= 0:
                    text_offset = found_pos
                    logger.debug(f"Offset ajustado: palavra '{word_text}' encontrada em {text_offset}")

                else:
                    text_offset = max(0, editor_text_len - 1)
                    logger.debug(f"Palavra '{word_text}' não encontrada, usando offset {text_offset}")

            if self._mode == HighlightMode.WORD:
                start_pos = text_offset
                end_pos = min(text_offset + word_length, editor_text_len)

            elif self._mode == HighlightMode.SENTENCE:
                start_pos, end_pos = self._get_sentence_bounds(text_offset)

            else:
                start_pos, end_pos = self._get_paragraph_bounds(text_offset)

            start_pos = max(0, min(start_pos, editor_text_len - 1))
            end_pos = max(start_pos + 1, min(end_pos, editor_text_len))

            if self._mode != HighlightMode.WORD:
                highlighted_text = editor_text[start_pos:end_pos][:50]
                logger.debug(f"Highlight {self._mode.value}: [{start_pos}:{end_pos}] = '{highlighted_text}...'")

            self._apply_highlight(start_pos, end_pos)
            self.word_highlighted.emit(start_pos, end_pos)

            if self._auto_scroll:
                self._scroll_to_position(start_pos)

        except Exception as e:
            logger.debug(f"Erro ao aplicar highlight no índice {index}: {e}", exc_info=True)

    def _get_word_bounds(self, offset: int, length: int) -> Tuple[int, int]:
        return offset, offset + length

    def _get_sentence_bounds(self, offset: int) -> Tuple[int, int]:
        try:
            text = self._text_edit.toPlainText()

            if not text:
                logger.debug("_get_sentence_bounds: texto vazio")
                return 0, 1

            if offset < 0:
                offset = 0

            if offset >= len(text):
                offset = len(text) - 1

            sentence_delimiters = '.!?'

            start = offset
            while start > 0:
                char = text[start - 1]
                if char in sentence_delimiters:
                    break

                if char == '\n':
                    break

                start -= 1

            while start < len(text) and text[start] in ' \t\n':
                start += 1

            if start > offset:
                start = offset

            end = offset
            while end < len(text):
                char = text[end]
                if char in sentence_delimiters:
                    end += 1
                    while end < len(text) and text[end] in sentence_delimiters:
                        end += 1

                    break

                if char == '\n':
                    break

                end += 1

            end = min(end, len(text))

            if end <= start:
                end = min(start + 1, len(text))

            logger.debug(f"_get_sentence_bounds: offset={offset}, start={start}, end={end}, len={end-start}")
            return start, end

        except Exception as e:
            logger.debug(f"Erro em _get_sentence_bounds: {e}", exc_info=True)
            return max(0, offset), max(1, offset + 1)

    def _get_paragraph_bounds(self, offset: int) -> Tuple[int, int]:
        try:
            text = self._text_edit.toPlainText()

            if not text:
                logger.debug("_get_paragraph_bounds: texto vazio")
                return 0, 1

            if offset < 0:
                offset = 0

            if offset >= len(text):
                offset = len(text) - 1

            start = offset
            while start > 0:
                if text[start - 1] == '\n':
                    if start >= 2 and text[start - 2] == '\n':
                        break

                    break

                start -= 1

            end = offset
            while end < len(text):
                if text[end] == '\n':
                    if end + 1 < len(text) and text[end + 1] == '\n':
                        break

                    break

                end += 1

            end = min(end, len(text))

            if end <= start:
                end = min(start + 1, len(text))

            logger.debug(f"_get_paragraph_bounds: offset={offset}, start={start}, end={end}, len={end-start}")
            return start, end

        except Exception as e:
            logger.debug(f"Erro em _get_paragraph_bounds: {e}", exc_info=True)
            return max(0, offset), max(1, offset + 1)

    def _apply_highlight(self, start_pos: int, end_pos: int):
        try:
            selections = []

            sel = QTextEdit.ExtraSelection()
            cursor = QTextCursor(self._text_edit.document())
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
            sel.cursor = cursor

            fmt = QTextCharFormat()
            fmt.setBackground(QColor(self._style.current_word_bg))
            fmt.setForeground(QColor(self._style.current_word_fg))

            if self._style.bold:
                fmt.setFontWeight(700)

            if self._style.underline:
                fmt.setFontUnderline(True)

            sel.format = fmt
            selections.append(sel)

            try:
                for prev_sel in self._previous_selections:
                    prev_start = prev_sel.cursor.selectionStart()
                    prev_end = prev_sel.cursor.selectionEnd()
                    if not (prev_start < end_pos and prev_end > start_pos):
                        selections.append(prev_sel)

            except Exception:
                pass

            self._text_edit.setExtraSelections(selections)

        except Exception as e:
            logger.debug(f"Erro ao aplicar highlight: {e}", exc_info=True)

    def _clear_highlight(self):
        try:
            self._text_edit.setExtraSelections([])

        except Exception:
            pass

    def _scroll_to_position(self, position: int):
        try:
            cursor = self._text_edit.textCursor()
            cursor.setPosition(position)
            self._text_edit.setTextCursor(cursor)
            self._text_edit.ensureCursorVisible()

        except Exception:
            pass


class SpeechHighlightSettings:
    DEFAULT_SETTINGS = {
        "enabled": True,
        "mode": "word",
        "auto_scroll": True,
        "background_color": "#FFEB3B",
        "text_color": "#000000",
        "current_word_bg": "#FF9800",
        "current_word_fg": "#000000",
        "underline": False,
        "bold": False,
    }

    @classmethod
    def get_default_style(cls) -> HighlightStyle:
        return HighlightStyle(
            background_color=cls.DEFAULT_SETTINGS["background_color"],
            text_color=cls.DEFAULT_SETTINGS["text_color"],
            current_word_bg=cls.DEFAULT_SETTINGS["current_word_bg"],
            current_word_fg=cls.DEFAULT_SETTINGS["current_word_fg"],
            underline=cls.DEFAULT_SETTINGS["underline"],
            bold=cls.DEFAULT_SETTINGS["bold"],
        )

    @classmethod
    def get_default_mode(cls) -> HighlightMode:
        mode_str = cls.DEFAULT_SETTINGS["mode"]
        return HighlightMode(mode_str)
