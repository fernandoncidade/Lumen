from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
from source.utils.FontManager import FontManager

logger = LogManager.get_logger()

def _reconstruir_paragrafos_pyppdf2(raw_text: str) -> str:
    lines = raw_text.splitlines()
    paragraphs = []
    cur = ""

    for line in lines:
        trimmed = line.strip()

        if trimmed == "":
            if cur:
                paragraphs.append(cur.strip())
                cur = ""

            continue

        if trimmed.endswith("-"):
            piece = trimmed[:-1]
            if cur:
                cur += piece

            else:
                cur = piece

            continue

        leading_tabs = line.startswith("\t")
        leading_spaces = len(line) - len(line.lstrip(" "))
        prev_ends_dot = cur.rstrip().endswith(".")
        starts_upper = bool(trimmed) and trimmed[0].isupper()

        if cur and prev_ends_dot and starts_upper and (leading_tabs or leading_spaces >= 4):
            cur = cur.rstrip() + "\n" + trimmed

        else:
            if cur:
                cur = cur.rstrip() + " " + trimmed

            else:
                cur = trimmed

    if cur:
        paragraphs.append(cur.strip())

    return "\n\n".join(paragraphs)

def carregar_pdf(self):
    arquivo, _ = QFileDialog.getOpenFileName(self, QCoreApplication.translate("App", "Selecionar PDF"), "", QCoreApplication.translate("App", "PDF Files (*.pdf)"))

    if not arquivo:
        try:
            self._last_pdf_path = None

        except Exception as e:
            logger.debug(f"Erro ao limpar caminho do PDF anterior: {e}", exc_info=True)

        return

    try:
        self._last_pdf_path = arquivo

    except Exception as e:
        logger.debug(f"Erro ao armazenar caminho do PDF: {e}", exc_info=True)
        self._last_pdf_path = None

    try:
        if getattr(self, "pdf_doc", None):
            try:
                load_res = self.pdf_doc.load(arquivo)
                try:
                    self._pdf_enable_toolbar(True)

                except Exception as e:
                    logger.debug(f"Erro ao habilitar toolbar PDF: {e}", exc_info=True)

                # Forçar exibição em modo "Largura" (continuous) ao carregar
                try:
                    # define modo e ajusta visualização para FitToWidth / continuous
                    if hasattr(self, "_pdf_zoom_fit_width"):
                        self._pdf_zoom_fit_width()
                    else:
                        try:
                            self._pdf_scroll_mode = "continuous"
                        except Exception:
                            pass
                except Exception as e:
                    logger.debug(f"Erro ao forçar modo Largura no carregamento: {e}", exc_info=True)

                try:
                    if hasattr(self, "_content_stack"):
                        self._content_stack.setCurrentIndex(1)

                except Exception as e:
                    logger.debug(f"Erro ao mostrar aba PDF: {e}", exc_info=True)

            except Exception as e:
                logger.debug(f"Falha ao carregar PDF no visualizador: {e}", exc_info=True)

    except Exception as e:
        logger.debug(f"Erro durante tentativa de usar pdf_doc: {e}", exc_info=True)

    try:
        try:
            import pdfplumber
            texto_completo = []

            with pdfplumber.open(arquivo) as pdf:
                for page in pdf.pages:
                    try:
                        words = page.extract_words()
                        if not words:
                            t = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
                            texto_completo.append(t)
                            continue

                        lines_map = {}
                        for w in words:
                            key = int(round(w.get("top", 0)))
                            lines_map.setdefault(key, []).append(w)

                        line_items = []
                        for top in sorted(lines_map.keys()):
                            ws = sorted(lines_map[top], key=lambda x: x.get("x0", 0))
                            line_text = " ".join(w.get("text", "") for w in ws).strip()
                            min_x = ws[0].get("x0", 0) if ws else 0
                            line_items.append((min_x, line_text))

                        page_paragraphs = []
                        cur = ""
                        prev_min_x = None
                        for min_x, line in line_items:
                            trimmed = (line or "").strip()
                            if trimmed == "":
                                if cur:
                                    page_paragraphs.append(cur.strip())
                                    cur = ""

                                prev_min_x = min_x
                                continue

                            INDENT_THRESHOLD_PX = 20
                            indented = min_x is not None and min_x >= INDENT_THRESHOLD_PX

                            prev_ends_dot = cur.rstrip().endswith(".")
                            starts_upper = bool(trimmed) and trimmed[0].isupper()

                            if cur and prev_ends_dot and starts_upper and indented:
                                cur = cur.rstrip() + "\n" + trimmed

                            else:
                                if cur:
                                    cur = cur.rstrip() + " " + trimmed

                                else:
                                    cur = trimmed

                            prev_min_x = min_x

                        if cur:
                            page_paragraphs.append(cur.strip())

                        texto_completo.append("\n\n".join(page_paragraphs))

                    except Exception:
                        t = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
                        texto_completo.append(t)

            final_text = "\n\n".join(texto_completo).strip()
            if final_text:
                self.texto_area.setPlainText(final_text)
                try:
                    self.texto_area.setFont(FontManager.get_font())

                except Exception as e:
                    logger.error(f"Erro ao aplicar fonte do FontManager: {e}", exc_info=True)

                try:
                    if hasattr(self, "_content_stack"):
                        self._content_stack.setCurrentIndex(0)

                except Exception as e:
                    logger.debug(f"Erro ao mostrar aba Texto: {e}", exc_info=True)

                return

        except Exception as e:
            logger.debug(f"pdfplumber indisponível ou falhou, tentando alternativa: {e}", exc_info=True)

        try:
            from pdfminer.high_level import extract_text
            from pdfminer.layout import LAParams

            laparams = LAParams(line_margin=0.5, char_margin=2.0, word_margin=0.1)
            texto = extract_text(arquivo, laparams=laparams) or ""
            texto = texto.strip()
            if texto:
                self.texto_area.setPlainText(texto)
                try:
                    self.texto_area.setFont(FontManager.get_font())

                except Exception as e:
                    logger.error(f"Erro ao aplicar fonte do FontManager: {e}", exc_info=True)

                try:
                    if hasattr(self, "_content_stack"):
                        self._content_stack.setCurrentIndex(0)

                except Exception as e:
                    logger.debug(f"Erro ao mostrar aba Texto: {e}", exc_info=True)

                return

        except Exception as e:
            logger.debug(f"pdfminer.six indisponível ou falhou, tentando PyPDF2: {e}", exc_info=True)

        try:
            from PyPDF2 import PdfReader

        except Exception as e:
            logger.error(f"Nenhuma biblioteca de extração de PDF disponível (pdfplumber/pdfminer/PyPDF2): {e}", exc_info=True)
            self.texto_area.setPlainText(QCoreApplication.translate("App", "Erro: nenhuma biblioteca de leitura de PDF encontrada. Instale 'pdfplumber' ou 'pdfminer.six' ou 'pypdf'.")) 

            try:
                if hasattr(self, "_content_stack"):
                    self._content_stack.setCurrentIndex(0)

            except Exception as e:
                logger.debug(f"Erro ao mostrar aba Texto: {e}", exc_info=True)

            return

        reader = PdfReader(arquivo)
        raw_pages = []
        for pagina in reader.pages:
            try:
                txt = pagina.extract_text() or ""

            except Exception as e:
                logger.debug(f"Erro ao extrair texto da página: {e}", exc_info=True)
                txt = ""

            raw_pages.append(txt)

        raw_all = "\n\n".join(raw_pages)
        final_text = _reconstruir_paragrafos_pyppdf2(raw_all)
        self.texto_area.setPlainText(final_text)

        try:
            self.texto_area.setFont(FontManager.get_font())

        except Exception as e:
            logger.error(f"Erro ao aplicar fonte do FontManager: {e}", exc_info=True)

        try:
            if hasattr(self, "_content_stack"):
                self._content_stack.setCurrentIndex(0)

        except Exception as e:
            logger.debug(f"Erro ao mostrar aba Texto: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao carregar PDF '{arquivo}': {str(e)}", exc_info=True)
        self.texto_area.setPlainText(QCoreApplication.translate("App", "Erro ao carregar PDF: {error}").format(error=str(e)))
        try:
            if hasattr(self, "_content_stack"):
                self._content_stack.setCurrentIndex(0)

        except Exception as e:
            logger.debug(f"Erro ao mostrar aba Texto: {e}", exc_info=True)
