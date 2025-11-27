import json
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def salvar_conceitos(self):
    try:
        with open(self.arquivo_conceitos, 'w', encoding='utf-8') as f:
            json.dump(self.conceitos, f, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Erro ao salvar conceitos no arquivo '{self.arquivo_conceitos}': {str(e)}", exc_info=True)
