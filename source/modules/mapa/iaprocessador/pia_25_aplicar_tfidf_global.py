from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _aplicar_tfidf_global(self, texto: str, arvore: Dict):
    try:
        def coletar_textos(no, textos_lista):
            if no.get('texto_puro'):
                textos_lista.append(no['texto_puro'])

            for filho in no.get('filhos', []):
                coletar_textos(filho, textos_lista)

        textos_corpus = []
        coletar_textos(arvore, textos_corpus)

        if len(textos_corpus) < 2:
            return

        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 3)
        )
        tfidf_matrix = vectorizer.fit_transform(textos_corpus)
        feature_names = vectorizer.get_feature_names_out()

        scores_tfidf = {}
        for i, nome in enumerate(feature_names):
            scores_tfidf[nome.lower()] = tfidf_matrix[:, i].mean()

        def aplicar_scores(no):
            for conceito in no.get('conceitos', []):
                texto_conceito = conceito['texto'].lower()
                if texto_conceito in scores_tfidf:
                    boost = scores_tfidf[texto_conceito] * 0.3
                    conceito['importancia'] = min(conceito['importancia'] + boost, 1.0)

            for filho in no.get('filhos', []):
                aplicar_scores(filho)

        aplicar_scores(arvore)
        logger.info("✓ TF-IDF aplicado para refinar importâncias")

    except Exception as e:
        logger.error(f"Erro ao aplicar TF-IDF: {e}", exc_info=True)
