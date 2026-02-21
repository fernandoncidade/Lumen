from typing import List
import re
import unicodedata
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _preprocessar_linhas(self, texto: str) -> List[str]:
    try:
        t = unicodedata.normalize('NFKC', texto or "")
        t = t.replace('\xa0', ' ')  # NBSP -> espaço
        t = t.replace('–', '-').replace('—', '-')  # EN/EM dash -> '-'
        t = re.sub(r'[ \t]+', ' ', t)
        return [ln.strip() for ln in t.split('\n')]

    except Exception as e:
        logger.error(f"Erro ao preprocessar linhas: {e}")
        return [ln.strip() for ln in (texto or "").split('\n')]
