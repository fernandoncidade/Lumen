from docx import Document
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def extrair_texto_docx(self, caminho: str) -> str:
    try:
        doc = Document(caminho)
        texto = "\n".join([paragrafo.text for paragrafo in doc.paragraphs])
        return texto

    except Exception as e:
        logger.error(f"Erro ao extrair texto do DOCX: {e}", exc_info=True)
        return ""
