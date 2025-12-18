from typing import Dict
import re
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _variantes_para_match(self, linha: str) -> Dict[str, str]:
    try:
        original = (linha or "").strip()
        sem_acentos = self._remover_acentos(original)
        condensada = re.sub(r"\s+", "", sem_acentos)
        return {
            "original": original,
            "sem_acentos": sem_acentos,
            "condensada": condensada,
        }

    except Exception as e:
        logger.error(f"Erro ao gerar variantes para match: {e}", exc_info=True)
        return {
            "original": linha or "",
            "sem_acentos": linha or "",
            "condensada": linha or "",
        }
