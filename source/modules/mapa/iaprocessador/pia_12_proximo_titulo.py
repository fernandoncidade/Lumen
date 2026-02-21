from typing import List
import re
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _proximo_titulo(self, linhas: List[str], idx: int) -> str:
    try:
        for j in range(idx + 1, min(idx + 6, len(linhas))):
            cand = linhas[j].strip()
            if not cand:
                continue

            if self._e_titulo_maiusculas(cand, linhas, j) or self._e_titulo_isolado(cand, linhas, j):
                return cand

            if 5 <= len(cand) <= 120 and re.match(r'^[A-ZÁÉÍÓÚÂÊÔÃÕÇ]', cand):
                return cand

        return ""

    except Exception as e:
        logger.error(f"Erro ao encontrar próximo título: {e}", exc_info=True)
        return ""
