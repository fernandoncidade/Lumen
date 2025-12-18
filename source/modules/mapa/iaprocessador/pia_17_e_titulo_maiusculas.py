from typing import List
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _e_titulo_maiusculas(self, linha: str, linhas: List[str], idx: int) -> bool:
    try:
        if not linha or len(linha) < 10 or len(linha) > 150:
            return False

        letras = [c for c in linha if c.isalpha()]
        if not letras:
            return False

        maiusculas = sum(1 for c in letras if c.isupper())
        taxa_maiusculas = maiusculas / len(letras)

        if taxa_maiusculas < 0.7:
            return False

        if linha.endswith((',', ';', '-')):
            return False

        linha_anterior = linhas[idx - 1].strip() if idx > 0 else ""
        linha_posterior = linhas[idx + 1].strip() if idx < len(linhas) - 1 else ""

        if not linha_anterior or not linha_posterior:
            return True

        if len(linha_posterior) > 0:
            primeira_letra_posterior = next((c for c in linha_posterior if c.isalpha()), None)
            if primeira_letra_posterior and primeira_letra_posterior.islower():
                return True

        return False

    except Exception as e:
        logger.error(f"Erro ao verificar título em maiúsculas: {e}", exc_info=True)
        return False
