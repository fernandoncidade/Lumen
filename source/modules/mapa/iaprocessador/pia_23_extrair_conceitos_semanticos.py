from typing import List, Dict
from collections import defaultdict
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _extrair_conceitos_semanticos(self, doc, texto: str, nivel: int) -> List[Dict]:
    try:
        conceitos = []
        entidades = defaultdict(list)
        for ent in doc.ents:
            if ent.label_ in ['PER', 'ORG', 'LOC', 'MISC', 'EVENT', 'PERSON', 'GPE', 'NORP']:
                entidades[ent.text.lower()].append(ent.sent.text.strip())

        for texto_ent, contextos in entidades.items():
            conceitos.append({
                'texto': texto_ent.title(),
                'tipo': 'entidade',
                'importancia': min(0.9, 0.7 + len(contextos) * 0.03),
                'frequencia': len(contextos),
                'contextos': contextos[:5]
            })

        termos = defaultdict(lambda: {'freq': 0, 'contextos': []})
        for chunk in doc.noun_chunks:
            if 2 <= len(chunk) <= 5:
                termo_texto = chunk.text.strip()
                termos[termo_texto]['freq'] += 1
                termos[termo_texto]['contextos'].append(chunk.sent.text.strip())

        for termo, dados in termos.items():
            if dados['freq'] >= 2:
                importancia = 0.5 + (len(termo.split()) * 0.1) + (min(dados['freq'], 10) * 0.03)
                conceitos.append({
                    'texto': termo,
                    'tipo': 'termo_tecnico',
                    'importancia': min(importancia, 0.95),
                    'frequencia': dados['freq'],
                    'contextos': dados['contextos'][:5]
                })

        substantivos = defaultdict(list)
        for token in doc:
            if token.pos_ == 'NOUN' and not token.is_stop and len(token.text) > 3:
                substantivos[token.lemma_.lower()].append(token.sent.text.strip())

        for lemma, contextos in substantivos.items():
            if len(contextos) >= 3:
                conceitos.append({
                    'texto': lemma.capitalize(),
                    'tipo': 'conceito',
                    'importancia': min(0.7, 0.4 + len(contextos) * 0.04),
                    'frequencia': len(contextos),
                    'contextos': contextos[:5]
                })

        conceitos = sorted(conceitos, key=lambda c: c['importancia'], reverse=True)
        limite = {0: 12, 1: 10, 2: 8, 3: 6, 4: 5}.get(nivel, 5)

        return conceitos[:limite]

    except Exception as e:
        logger.error(f"Erro ao extrair conceitos semânticos: {e}", exc_info=True)
        return []
