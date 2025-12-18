import pdfplumber
import unicodedata
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def extrair_texto_pdf(self, caminho: str) -> str:
    try:
        partes = []
        with pdfplumber.open(caminho) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3,
                    layout=True,
                    x_density=7.25,
                    y_density=13
                ) or ""

                page_text = unicodedata.normalize('NFKC', page_text)
                page_text = page_text.strip()

                if page_text:
                    partes.append(page_text)

        texto_completo = "\n\n".join(partes)
        texto_completo = self._corrigir_caracteres_extraidos(texto_completo)

        return texto_completo

    except Exception as e:
        logger.error(f"Erro ao extrair texto do PDF (pdfplumber): {e}", exc_info=True)
        return ""
