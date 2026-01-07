from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
from source.utils.FontManager import FontManager
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
                    self._pdf_zoom_fit_width()

                except Exception as e:
                    logger.debug(f"Erro ao aplicar zoom largura: {e}", exc_info=True)

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
