import spacy
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _carregar_modelo_nlp(self):
    try:
        try:
            self.nlp = spacy.load("pt_core_news_lg")
            self.idioma_detectado = 'pt'
            logger.info("Modelo pt_core_news_lg carregado")

        except OSError:
            try:
                self.nlp = spacy.load("en_core_web_lg")
                self.idioma_detectado = 'en'
                logger.info("Modelo en_core_web_lg carregado (fallback)")

            except OSError:
                self.nlp = spacy.load("pt_core_news_sm")
                self.idioma_detectado = 'pt'
                logger.warning("Usando modelo pequeno pt_core_news_sm")

        self.nlp.max_length = 2_000_000
        logger.info(
            f"NLP configurado: idioma={self.idioma_detectado}, max_length={self.nlp.max_length}"
        )

    except Exception as e:
        logger.error(f"Erro ao carregar modelo spaCy: {e}", exc_info=True)
        raise
