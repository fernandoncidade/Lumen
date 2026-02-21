from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _extrair_conceitos_tfidf(self, doc, texto: str, max_conceitos: int = 15) -> List[Dict]:
    try:
        sentencas = [s.text.strip() for s in doc.sents if s.text.strip()]
        if not sentencas:
            sentencas = [texto]

        vectorizer = TfidfVectorizer(
            max_features=300,
            stop_words="english" if self.idioma_detectado == "en" else None,
            ngram_range=(1, 3),
        )
        tfidf = vectorizer.fit_transform(sentencas)
        features = vectorizer.get_feature_names_out()
        scores = tfidf.mean(axis=0).A1
        termos_scores = sorted(zip(features, scores), key=lambda x: x[1], reverse=True)

        conceitos = []
        usados = set()

        def contexto_para(termo: str) -> List[str]:
            termo_lower = termo.lower()
            ctx = []
            for s in sentencas:
                if termo_lower in s.lower():
                    ctx.append(s)
                    if len(ctx) >= 5:
                        break

            return ctx

        try:
            noun_chunks = set([nc.text.strip().lower() for nc in doc.noun_chunks if len(nc) <= 6])

        except Exception:
            noun_chunks = set()

        for termo, score in termos_scores[: max_conceitos * 2]:
            t = termo.strip()
            if len(t) < 3 or t in usados:
                continue

            tipo = "termo_tecnico" if t in noun_chunks or len(t.split()) >= 2 else "conceito"
            ctx = contexto_para(t)
            frequencia = sum(s.lower().count(t.lower()) for s in sentencas)
            importancia = min(0.4 + score * 0.8 + (0.05 if tipo == "termo_tecnico" else 0), 1.0)

            conceitos.append({
                "texto": t,
                "tipo": tipo,
                "importancia": float(importancia),
                "frequencia": int(frequencia),
                "contextos": ctx,
            })
            usados.add(t)

            if len(conceitos) >= max_conceitos:
                break

        if not conceitos:
            conceitos = self._extrair_conceitos_semanticos(doc, texto, nivel=0)

        return conceitos

    except Exception as e:
        logger.error(f"Erro em _extrair_conceitos_tfidf: {e}", exc_info=True)
        return []
