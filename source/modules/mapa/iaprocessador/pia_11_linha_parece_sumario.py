import re
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _linha_parece_sumario(self, linha: str) -> bool:
    try:
        if re.search(r'\.{4,}\s*\d{1,4}$', linha):
            return True

        return False

    except Exception as e:
        logger.error(f"Erro ao analisar linha para sumário: {e}", exc_info=True)
        return False
