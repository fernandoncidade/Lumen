from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def extrair_texto_txt(self, caminho: str) -> str:
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()

    except Exception as e:
        logger.error(f"Erro ao extrair texto do TXT: {e}", exc_info=True)
        return ""
