from __future__ import annotations
from typing import List, Tuple
from PySide6.QtGui import QTextCursor, QTextDocument, QColor
from PySide6.QtWidgets import QTextEdit
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _text_find_show(self):
    try:
        if getattr(self, "_text_find_bar", None) is None:
            return

        if getattr(self, "texto_area", None) is None:
            return

        self._text_find_bar.show_bar()

    except Exception as e:
        logger.error(f"Erro ao abrir busca do Texto: {e}", exc_info=True)

def _text_find_toggle(self):
    try:
        bar = getattr(self, "_text_find_bar", None)
        if bar is None or getattr(self, "texto_area", None) is None:
            return

        if bar.isVisible():
            bar.hide_bar()

        else:
            bar.show_bar()

    except Exception as e:
        logger.debug(f"Erro ao alternar busca do Texto: {e}", exc_info=True)

def _text_find_clear(self):
    try:
        self._text_find_hits = []
        self._text_find_hit_cursor = -1

        ta = getattr(self, "texto_area", None)
        if ta is not None:
            try:
                ta.setExtraSelections([])

            except Exception:
                pass

        if getattr(self, "_text_find_bar", None) is not None:
            self._text_find_bar.update_count(0, 0)

    except Exception as e:
        logger.debug(f"Erro ao limpar busca do Texto: {e}", exc_info=True)

def _text_find_set_highlight_all(self, enable: bool):
    try:
        self._text_find_highlight_all = bool(enable)
        _text_find_apply(
            self,
            (getattr(self, "_text_find_query", "") or "").strip(),
            match_case=bool(getattr(self, "_text_find_match_case", False)),
            whole_words=bool(getattr(self, "_text_find_whole_words", False)),
        )

    except Exception:
        pass

def _text_find_apply(self, query: str, match_case: bool = False, whole_words: bool = False):
    try:
        ta: QTextEdit | None = getattr(self, "texto_area", None)
        if ta is None:
            return

        q = (query or "").strip()
        self._text_find_query = q
        self._text_find_match_case = bool(match_case)
        self._text_find_whole_words = bool(whole_words)

        if not q:
            _text_find_clear(self)
            return

        doc: QTextDocument = ta.document()

        flags = QTextDocument.FindFlags()
        if match_case:
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        if whole_words:
            flags |= QTextDocument.FindFlag.FindWholeWords

        hits: List[Tuple[int, int]] = []
        cur = QTextCursor(doc)
        cur.movePosition(QTextCursor.MoveOperation.Start)

        while True:
            cur = doc.find(q, cur, flags)
            if cur.isNull():
                break

            hits.append((cur.selectionStart(), cur.selectionEnd()))

        self._text_find_hits = hits
        self._text_find_hit_cursor = 0 if hits else -1

        if hits:
            start, end = hits[0]
            c = ta.textCursor()
            c.setPosition(start)
            c.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            ta.setTextCursor(c)
            ta.ensureCursorVisible()

        _text_find_apply_highlights(self)

        if getattr(self, "_text_find_bar", None) is not None:
            self._text_find_bar.update_count(1 if hits else 0, len(hits))

    except Exception as e:
        logger.error(f"Erro ao aplicar busca no Texto: {e}", exc_info=True)
        _text_find_clear(self)

def _text_find_next(self):
    try:
        hits = list(getattr(self, "_text_find_hits", []) or [])
        if not hits:
            return

        idx = int(getattr(self, "_text_find_hit_cursor", 0))
        idx = (idx + 1) % len(hits)
        self._text_find_hit_cursor = idx

        _text_find_goto_hit(self, idx)

    except Exception as e:
        logger.debug(f"Erro ao ir para próximo resultado (Texto): {e}", exc_info=True)

def _text_find_prev(self):
    try:
        hits = list(getattr(self, "_text_find_hits", []) or [])
        if not hits:
            return

        idx = int(getattr(self, "_text_find_hit_cursor", 0))
        idx = (idx - 1) % len(hits)
        self._text_find_hit_cursor = idx

        _text_find_goto_hit(self, idx)

    except Exception as e:
        logger.debug(f"Erro ao ir para resultado anterior (Texto): {e}", exc_info=True)

def _text_find_goto_hit(self, idx: int):
    ta = getattr(self, "texto_area", None)
    if ta is None:
        return

    hits = list(getattr(self, "_text_find_hits", []) or [])
    if not hits:
        return

    idx = max(0, min(int(idx), len(hits) - 1))
    start, end = hits[idx]

    c = ta.textCursor()
    c.setPosition(start)
    c.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    ta.setTextCursor(c)
    ta.ensureCursorVisible()

    _text_find_apply_highlights(self)

    if getattr(self, "_text_find_bar", None) is not None:
        self._text_find_bar.update_count(idx + 1, len(hits))

def _text_find_apply_highlights(self):
    ta: QTextEdit | None = getattr(self, "texto_area", None)
    if ta is None:
        return

    hits = list(getattr(self, "_text_find_hits", []) or [])
    if not hits:
        try:
            ta.setExtraSelections([])

        except Exception:
            pass

        return

    highlight_all = bool(getattr(self, "_text_find_highlight_all", True))
    cur_idx = int(getattr(self, "_text_find_hit_cursor", -1))

    sels: List[QTextEdit.ExtraSelection] = []

    def _make_sel(start: int, end: int, color_hex: str):
        sel = QTextEdit.ExtraSelection()
        c = QTextCursor(ta.document())
        c.setPosition(start)
        c.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        sel.cursor = c
        sel.format.setBackground(QColor(color_hex))
        return sel

    if highlight_all:
        for i, (s, e) in enumerate(hits):
            if i == cur_idx:
                continue

            sels.append(_make_sel(s, e, "#FFEB3B"))

    if 0 <= cur_idx < len(hits):
        s, e = hits[cur_idx]
        sels.append(_make_sel(s, e, "#FF9800"))

    try:
        ta.setExtraSelections(sels)

    except Exception:
        pass
