from typing import List, Dict, Tuple
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _identificar_relacoes_semanticas(self, arvore: Dict) -> List[Tuple[str, str, str]]:
    try:
        relacoes = []

        def coletar_conceitos(no, conceitos_set):
            for c in no.get('conceitos', []):
                conceitos_set.add(c['texto'].lower())

            for filho in no.get('filhos', []):
                coletar_conceitos(filho, conceitos_set)

        conceitos_globais = set()
        coletar_conceitos(arvore, conceitos_globais)

        def analisar_relacoes(no):
            for conceito in no.get('conceitos', []):
                for contexto in conceito.get('contextos', [])[:3]:
                    doc_ctx = self.nlp(contexto[:1000])

                    for token in doc_ctx:
                        if token.dep_ in ['nsubj', 'nsubjpass'] and token.head.pos_ == 'VERB':
                            sujeito = token.text.lower()
                            verbo = token.head.lemma_

                            for child in token.head.children:
                                if child.dep_ in ['dobj', 'attr', 'pobj']:
                                    objeto = child.text.lower()

                                    if sujeito in conceitos_globais and objeto in conceitos_globais:
                                        relacoes.append((sujeito, verbo, objeto))

            for filho in no.get('filhos', []):
                analisar_relacoes(filho)

        analisar_relacoes(arvore)
        return list(set(relacoes))[:40]

    except Exception as e:
        logger.error(f"Erro ao identificar relações semânticas: {e}", exc_info=True)
        return []
