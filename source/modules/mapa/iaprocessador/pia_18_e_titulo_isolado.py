from typing import List
import re
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _e_titulo_isolado(self, linha: str, linhas: List[str], idx: int) -> bool:
    try:
        if not linha or len(linha) < 15 or len(linha) > 120:
            return False

        primeira_letra = next((c for c in linha if c.isalpha()), None)
        if not primeira_letra or not primeira_letra.isupper():
            return False

        if re.match(r'^[\d\.\s\-]+$', linha):
            return False

        if linha.endswith('.'):
            return False

        linha_anterior = linhas[idx - 1].strip() if idx > 0 else ""
        linha_posterior = linhas[idx + 1].strip() if idx < len(linhas) - 1 else ""

        if linha_anterior and len(linha_anterior) > 10:
            return False

        if linha_posterior:
            primeira_posterior = next((c for c in linha_posterior if c.isalpha()), None)
            if primeira_posterior and primeira_posterior.islower():
                return False

        return True

    except Exception as e:
        logger.error(f"Erro ao verificar título isolado: {e}", exc_info=True)
        return False
