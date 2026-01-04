from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _pdf_find_show(self):
    try:
        bar = getattr(self, "_pdf_find_bar", None)
        if bar is None or getattr(self, "pdf_view", None) is None:
            return

        bar.show_bar()

    except Exception as e:
        logger.error(f"Erro ao abrir busca do PDF: {e}", exc_info=True)

def _pdf_find_toggle(self):
    try:
        bar = getattr(self, "_pdf_find_bar", None)
        if bar is None or getattr(self, "pdf_view", None) is None:
            return

        if bar.isVisible():
            bar.hide_bar()

        else:
            bar.show_bar()

    except Exception as e:
        logger.debug(f"Erro ao alternar busca do PDF: {e}", exc_info=True)

def _pdf_find_clear(self):
    try:
        if getattr(self, "pdf_view", None) is None:
            return

        self.pdf_view.clear_search()

        bar = getattr(self, "_pdf_find_bar", None)
        if bar is not None:
            bar.update_count(0, 0)

    except Exception as e:
        logger.debug(f"Erro ao limpar busca do PDF: {e}", exc_info=True)

def _pdf_find_set_highlight_all(self, enable: bool):
    try:
        if getattr(self, "pdf_view", None) is None:
            return

        self.pdf_view.set_highlight_all(bool(enable))

    except Exception:
        pass

def _pdf_find_apply(self, query: str, match_case: bool = False, whole_words: bool = False):
    try:
        if getattr(self, "pdf_view", None) is None:
            return

        total = self.pdf_view.search(query, match_case=bool(match_case), whole_words=bool(whole_words))
        cur, tot = self.pdf_view.current_hit_position()

        bar = getattr(self, "_pdf_find_bar", None)
        if bar is not None:
            bar.update_count(cur if total else 0, tot if total else 0)

    except Exception as e:
        logger.error(f"Erro ao aplicar busca do PDF: {e}", exc_info=True)
        _pdf_find_clear(self)

def _pdf_find_next(self):
    try:
        if getattr(self, "pdf_view", None) is None:
            return

        self.pdf_view.goto_next_hit()
        cur, tot = self.pdf_view.current_hit_position()

        bar = getattr(self, "_pdf_find_bar", None)
        if bar is not None:
            bar.update_count(cur, tot)

    except Exception:
        pass

def _pdf_find_prev(self):
    try:
        if getattr(self, "pdf_view", None) is None:
            return

        self.pdf_view.goto_prev_hit()
        cur, tot = self.pdf_view.current_hit_position()

        bar = getattr(self, "_pdf_find_bar", None)
        if bar is not None:
            bar.update_count(cur, tot)

    except Exception:
        pass
