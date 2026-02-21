import unicodedata
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _remover_acentos(self, s: str) -> str:
    try:
        if not s:
            return ""

        nfkd = unicodedata.normalize("NFKD", s)
        return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

    except Exception as e:
        logger.error(f"Erro ao remover acentos: {e}")
        return s or ""
