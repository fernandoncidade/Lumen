import json
import os
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def carregar_conceitos(self):
    try:
        if os.path.exists(self.arquivo_conceitos):
            with open(self.arquivo_conceitos, 'r', encoding='utf-8') as f:
                return json.load(f)

        return []

    except Exception as e:
        logger.error(f"Erro ao carregar conceitos do arquivo '{self.arquivo_conceitos}': {str(e)}", exc_info=True)
        return []
