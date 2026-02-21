from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _detectar_idioma_texto(self, texto: str) -> str:
    try:
        palavras_pt = ['capítulo', 'seção', 'introdução', 'conclusão', 'parte', 'português']
        palavras_en = ['chapter', 'section', 'introduction', 'conclusion', 'part', 'english']

        texto_lower = texto.lower()[:5000]

        score_pt = sum(1 for p in palavras_pt if p in texto_lower)
        score_en = sum(1 for p in palavras_en if p in texto_lower)

        return 'pt' if score_pt > score_en else 'en'

    except Exception as e:
        logger.error(f"Erro ao detectar idioma do texto: {e}", exc_info=True)
        return 'desconhecido'
