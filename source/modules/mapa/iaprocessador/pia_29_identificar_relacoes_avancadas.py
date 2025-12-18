from typing import List, Dict, Tuple
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _identificar_relacoes_avancadas(self, doc, conceitos: List[Dict]) -> List[Tuple[str, str, str]]:
    try:
        conceitos_set = {c['texto'].lower() for c in conceitos}
        relacoes = set()

        for sent in doc.sents:
            tokens = list(sent)
            for token in tokens:
                if token.pos_ == 'VERB':
                    sujeito = None
                    objeto = None

                    for child in token.children:
                        if child.dep_ in ('nsubj', 'nsubjpass') and not child.is_stop:
                            sujeito = child

                        if child.dep_ in ('dobj', 'obj', 'attr', 'pobj') and not child.is_stop:
                            objeto = child

                    if sujeito and objeto:
                        subj_txt = sujeito.text.lower()
                        obj_txt = objeto.text.lower()

                        subj_match = next((c for c in conceitos_set if subj_txt in c or c in subj_txt), None)
                        obj_match = next((c for c in conceitos_set if obj_txt in c or c in obj_txt), None)

                        if subj_match and obj_match and subj_match != obj_match:
                            relacoes.add((subj_match, token.lemma_.lower(), obj_match))

        return list(relacoes)

    except Exception as e:
        logger.error(f"Erro em _identificar_relacoes_avancadas: {e}", exc_info=True)
        return []
