from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
from source.utils.FontManager import FontManager
import re
logger = LogManager.get_logger()

_pdfplumber = None
_pypdf = None

try:
    import pdfplumber as _pdfplumber

except ImportError:
    pass

try:
    import pypdf as _pypdf

except ImportError:
    try:
        import PyPDF2 as _pypdf

    except ImportError:
        pass

def _extrair_texto_pdfplumber(arquivo: str) -> str:
    if not _pdfplumber:
        return ""

    try:
        with _pdfplumber.open(arquivo) as pdf:
            parts = []
            for page in pdf.pages:
                try:
                    text = page.extract_text() or ""
                    if text.strip():
                        parts.append(text.strip())

                except Exception:
                    continue

            return "\n\n".join(parts)

    except Exception as e:
        logger.debug(f"Falha ao extrair texto via pdfplumber: {e}", exc_info=True)
        return ""

def _extrair_texto_pypdf(arquivo: str) -> str:
    if not _pypdf:
        return ""

    try:
        with open(arquivo, "rb") as f:
            reader = _pypdf.PdfReader(f)
            parts = []
            for page in reader.pages:
                try:
                    text = page.extract_text() or ""
                    if text.strip():
                        parts.append(text.strip())

                except Exception:
                    continue

            return "\n\n".join(parts)

    except Exception as e:
        logger.debug(f"Falha ao extrair texto via pypdf: {e}", exc_info=True)
        return ""

_BULLET_PREFIX_RE = re.compile(r"^(?:[\-\*•●○▪▫‣∙►◆■□☐☑✓✔]|\d+[\)\.\:]|[A-Za-z][\)\.])\s+")
_SUB_BULLET_RE = re.compile(r"^[○◦\-–—►▸▹]\s+")
_UPPER_HEADING_RE = re.compile(r"^[A-ZÀ-Ü0-9 \-–—]{8,}$")
_SUBTITLE_KEYWORDS_RE = re.compile(
    r"^(?:O Papel d[eo]|Adequação|Limitações|Outros|Como|Notas|Problemas|Conclusão|Resumo|"
    r"Detalhamento|Agradecimentos|Arquivos|Em suma|Em resumo|Aqui está|Esse|Este|"
    r"Por que|Qual Seria|Como Seria)\b",
    re.IGNORECASE
)
_NUMBERED_QUESTION_RE = re.compile(r"^\d+\)\s+")
_NUMBERED_SECTION_RE = re.compile(r"^\d+\.\s+[A-ZÀ-Ü]")
_MULTI_NL_RE = re.compile(r"\n{3,}")

def _looks_like_bullet(line: str) -> bool:
    s = (line or "").lstrip()
    return bool(_BULLET_PREFIX_RE.match(s))

def _looks_like_sub_bullet(line: str) -> bool:
    s = (line or "").lstrip()
    return bool(_SUB_BULLET_RE.match(s))

def _looks_like_heading(line: str) -> bool:
    s = (line or "").strip()
    if len(s) < 8:
        return False

    if _UPPER_HEADING_RE.match(s) and len(s.split()) <= 12:
        return True

    return False

def _looks_like_subtitle(line: str) -> bool:
    s = (line or "").strip()
    if not s:
        return False

    if _SUBTITLE_KEYWORDS_RE.match(s):
        return True

    if _NUMBERED_SECTION_RE.match(s):
        return True

    if _NUMBERED_QUESTION_RE.match(s):
        return True

    return False

def _strip_trailing_closers(s: str) -> str:
    closers = ")]}\"'»\u201d\u2019"
    t = (s or "").rstrip()
    while t and t[-1] in closers:
        t = t[:-1].rstrip()

    return t

def _ends_sentence(line: str) -> bool:
    s = _strip_trailing_closers(line)
    if not s:
        return False

    tail = s.split()[-1].lower() if s.split() else ""
    abbrevs = {
        "sr.", "sra.", "dr.", "dra.", "prof.", "profa.", "etc.", "ex.", "obs.",
        "p.", "pp.", "vol.", "ed.", "cid", "f90.0", "6a02.0", "n.", "nº", "art."
    }
    if tail in abbrevs:
        return False

    return s.endswith((".", "?", "!", ":", ";", "…"))

def _reflow_pdf_text(text: str) -> str:
    if not text:
        return ""

    t = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = t.split("\n")

    out: list[str] = []
    pending = ""

    def flush_pending():
        nonlocal pending
        if pending.strip():
            out.append(pending.strip())

        pending = ""

    def ensure_blank_before():
        if out and out[-1] != "":
            out.append("")

    for raw in lines:
        line = (raw or "").strip()

        if not line:
            flush_pending()
            if out and out[-1] != "":
                out.append("")

            continue

        if _looks_like_subtitle(line):
            flush_pending()
            ensure_blank_before()
            out.append(line)
            continue

        if _looks_like_bullet(line) or _looks_like_heading(line):
            flush_pending()
            out.append(line)
            continue

        if _looks_like_sub_bullet(line):
            flush_pending()
            out.append(line)
            continue

        if not pending:
            pending = line
            continue

        if pending.endswith("-") and line and line[0].islower():
            pending = pending[:-1] + line
            continue

        if _ends_sentence(pending):
            flush_pending()
            pending = line

        else:
            pending = pending + " " + line

    flush_pending()

    result = "\n".join(out).strip()
    result = _MULTI_NL_RE.sub("\n\n", result)
    return result

def carregar_pdf(self):
    arquivo, _ = QFileDialog.getOpenFileName(
        self,
        QCoreApplication.translate("App", "Selecionar PDF"),
        "",
        QCoreApplication.translate("App", "PDF Files (*.pdf)")
    )

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
        if getattr(self, "pdf_view", None):
            ok = self.pdf_view.load_pdf(arquivo)
            if ok:
                try:
                    self._pdf_enable_toolbar(True)

                except Exception as e:
                    logger.debug(f"Erro ao habilitar toolbar PDF: {e}", exc_info=True)

                try:
                    try:
                        if getattr(self, "pdf_view", None) and hasattr(self.pdf_view, "setZoomFactor"):
                            self.pdf_view.setZoomFactor(1.0)

                        else:
                            try:
                                self._pdf_zoom_fit_width()

                            except Exception:
                                pass

                    except Exception:
                        pass

                except Exception as e:
                    logger.debug(f"Erro ao aplicar zoom padrão (100%): {e}", exc_info=True)

                try:
                    if hasattr(self, "_content_stack"):
                        self._content_stack.setCurrentIndex(1)

                except Exception as e:
                    logger.debug(f"Erro ao mostrar aba PDF: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Falha ao carregar PDF no visualizador: {e}", exc_info=True)

    final_text = ""
    final_text = _extrair_texto_pdfplumber(arquivo)

    if not final_text:
        final_text = _extrair_texto_pypdf(arquivo)

    if final_text:
        final_text = _reflow_pdf_text(final_text)
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

    else:
        logger.warning(f"Não foi possível extrair texto do PDF: {arquivo}")
