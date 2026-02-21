from typing import List, Dict
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _extrair_ideias_principais(self, doc, texto: str, nivel: int) -> List[Dict]:
    try:
        ideias = []
        palavras_indicadoras_pt = {
            'importante', 'fundamental', 'essencial', 'principal', 'crucial', 
            'necessário', 'deve', 'pode', 'permite', 'define', 'caracteriza'
        }

        palavras_indicadoras_en = {
            'important', 'fundamental', 'essential', 'main', 'crucial',
            'necessary', 'must', 'can', 'allows', 'defines', 'characterizes'
        }

        palavras_indicadoras = palavras_indicadoras_pt | palavras_indicadoras_en
        paragrafos = texto.split('\n\n')

        for para_idx, paragrafo in enumerate(paragrafos):
            if len(paragrafo.strip()) < 50:
                continue

            doc_para = self.nlp(paragrafo[:10000])
            sentencas = list(doc_para.sents)

            for sent_idx, sent in enumerate(sentencas):
                sent_texto = sent.text.strip()

                if not (20 <= len(sent_texto) <= 300):
                    continue

                score = 0.0

                if sent_idx == 0:
                    score += 0.3

                elif sent_idx == len(sentencas) - 1:
                    score += 0.2

                comp_ideal = 100
                dif_comp = abs(len(sent_texto) - comp_ideal)
                score += max(0, 0.2 - (dif_comp / 500))

                substantivos = [t for t in sent if t.pos_ in ['NOUN', 'PROPN']]
                verbos = [t for t in sent if t.pos_ == 'VERB']
                densidade = (len(substantivos) + len(verbos)) / max(len(sent), 1)
                score += min(densidade * 0.3, 0.3)

                texto_lower = sent_texto.lower()
                indicadores_presentes = sum(1 for p in palavras_indicadoras if p in texto_lower)
                score += min(indicadores_presentes * 0.15, 0.3)

                pos_doc = 1.0 - (para_idx / max(len(paragrafos), 1))
                score += pos_doc * 0.2

                ideias.append({
                    'texto': sent_texto,
                    'tipo': 'ideia_principal',
                    'importancia': min(score, 1.0),
                    'paragrafo': para_idx,
                    'posicao_sentenca': sent_idx
                })

        ideias = sorted(ideias, key=lambda i: i['importancia'], reverse=True)
        limite = {0: 8, 1: 6, 2: 5, 3: 4, 4: 3}.get(nivel, 3)

        return ideias[:limite]

    except Exception as e:
        logger.error(f"Erro ao extrair ideias principais: {e}", exc_info=True)
        return []
