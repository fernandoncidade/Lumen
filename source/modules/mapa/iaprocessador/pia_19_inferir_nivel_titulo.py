import re
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _inferir_nivel_titulo(self, titulo: str, nivel_anterior: int, tem_parte: bool) -> int:
    try:
        if re.match(r'(?:PARTE|PART)', titulo, re.IGNORECASE):
            return 1

        if tem_parte:
            if nivel_anterior == 1:
                return 2

            return min(nivel_anterior + 1, 4)

        return 2

    except Exception as e:
        logger.error(f"Erro ao inferir nível do título: {e}", exc_info=True)
        return nivel_anterior + 1
