from typing import List, Dict, Any
import re
from source.utils.LogManager import LogManager
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logger = LogManager.get_logger()


def _split_clauses_by_commas(sentence: str) -> List[str]:
    parts = [p.strip() for p in sentence.split(',') if p.strip()]
    return parts


def _detect_coordination_spacy(doc_sent, idioma: str) -> Dict[str, Any]:
    is_sindetic = False
    is_assindetic = False
    clauses = []

    try:
        has_cc = any(tok.dep_ == 'cc' for tok in doc_sent)
        has_conj = any(tok.dep_ == 'conj' for tok in doc_sent)
        if has_cc or has_conj:
            is_sindetic = True

        text = doc_sent.text
        comma_parts = _split_clauses_by_commas(text)
        if len(comma_parts) >= 2 and not is_sindetic:
            long_parts = [p for p in comma_parts if len(p.split()) >= 2]
            if len(long_parts) >= 2:
                is_assindetic = True
                clauses = long_parts

        if is_sindetic and not clauses:
            toks = list(doc_sent)
            splits = []
            current = []
            for t in toks:
                if t.dep_ == 'cc':
                    if current:
                        splits.append(' '.join([tt.text for tt in current]).strip())
                        current = []

                else:
                    current.append(t)

            if current:
                splits.append(' '.join([tt.text for tt in current]).strip())

            clauses = [s for s in splits if s]

    except Exception:
        txt = doc_sent.text.lower()
        conj_pt = r"\b(e|ou|mas|porém|contudo|todavia)\b"
        conj_en = r"\b(and|or|but|however|yet)\b"
        if idioma.startswith('pt'):
            if re.search(conj_pt, txt):
                is_sindetic = True

        else:
            if re.search(conj_en, txt):
                is_sindetic = True

        comma_parts = _split_clauses_by_commas(doc_sent.text)
        if len(comma_parts) >= 2 and not is_sindetic:
            is_assindetic = True
            clauses = comma_parts

    return {
        'is_sindetic': is_sindetic,
        'is_assindetic': is_assindetic,
        'clauses': clauses,
    }


def gerar_resumo_avancado(self, caminho_arquivo: str, top_n: int = 5) -> Dict[str, Any]:
    try:
        texto = None
        try:
            texto = self.extrair_texto(caminho_arquivo)

        except Exception:
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                texto = f.read()

        if not texto:
            return {'summary': '', 'sentences': []}

        idioma = self._detectar_idioma_texto(texto) if hasattr(self, '_detectar_idioma_texto') else getattr(self, 'idioma_detectado', 'pt')

        if getattr(self, 'nlp', None) is None:
            try:
                self._carregar_modelo_nlp()

            except Exception:
                pass

        doc = None
        try:
            doc = self.nlp(texto)

        except Exception:
            sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", texto) if s.strip()]
            class _S: pass
            class _Doc:
                def __init__(self, sents):
                    self.sents = [type('X', (), {'text': t})() for t in sents]

            doc = _Doc(sents)

        sents = [s for s in getattr(doc, 'sents', [])]
        if not sents:
            return {'summary': '', 'sentences': []}

        sent_texts = [s.text.strip() for s in sents if len(s.text.strip()) > 15]
        if not sent_texts:
            sent_texts = [s.text.strip() for s in sents]

        try:
            stop_words = 'english' if idioma.startswith('en') else None
            vectorizer = TfidfVectorizer(stop_words=stop_words)
            X = vectorizer.fit_transform(sent_texts)
            sim = (X * X.T).toarray()
            for i in range(sim.shape[0]):
                sim[i, i] = 0.0

            n = sim.shape[0]
            if n == 0:
                return {'summary': '', 'sentences': []}

            scores = [1.0 / n] * n
            damping = 0.85
            for _ in range(40):
                new_scores = [ (1 - damping) / n ] * n
                for i in range(n):
                    row = sim[:, i]
                    s_total = float(row.sum())
                    if s_total <= 0:
                        continue

                    contribution = row / s_total
                    for j in range(n):
                        new_scores[i] += damping * contribution[j] * scores[j]

                scores = new_scores

            tfidf_scores = np.array(scores, dtype=float)

            emb_scores = None
            try:
                get_emb_fn = getattr(self, '_get_sentence_embeddings', None)
                if get_emb_fn is None:
                    get_emb_fn = getattr(self, 'get_sentence_embeddings', None)

                if get_emb_fn is not None:
                    embs = get_emb_fn(sent_texts)
                    if embs is not None and len(embs) == len(sent_texts):
                        doc_emb = np.mean(embs, axis=0)
                        denom = (np.linalg.norm(embs, axis=1) * (np.linalg.norm(doc_emb) + 1e-9)) + 1e-9
                        emb_scores = np.dot(embs, doc_emb) / denom

            except Exception:
                emb_scores = None

            def _normalize(arr):
                arr = np.array(arr, dtype=float)
                if arr.size == 0:
                    return arr

                mn = arr.min()
                mx = arr.max()
                if mx - mn < 1e-9:
                    return np.ones_like(arr)

                return (arr - mn) / (mx - mn)

            norm_tfidf = _normalize(tfidf_scores)
            if emb_scores is None:
                combined = norm_tfidf

            else:
                norm_emb = _normalize(emb_scores)
                tfidf_w = 0.6
                emb_w = 0.4
                combined = tfidf_w * norm_tfidf + emb_w * norm_emb

            scored = list(zip(range(len(sent_texts)), sent_texts, combined.tolist()))
            scored.sort(key=lambda x: x[2], reverse=True)
            top = scored[:min(top_n, len(scored))]

            sentences_out = []
            for idx, text, sc in top:
                doc_sent = None
                try:
                    for s in sents:
                        if s.text.strip() == text:
                            doc_sent = s
                            break

                except Exception:
                    doc_sent = None

                coord = _detect_coordination_spacy(doc_sent if doc_sent is not None else type('Y', (), {'text': text}), idioma)
                sentences_out.append({
                    'index': idx,
                    'text': text,
                    'score': float(sc),
                    'is_sindetic': coord.get('is_sindetic', False),
                    'is_assindetic': coord.get('is_assindetic', False),
                    'clauses': coord.get('clauses', []),
                })

            sentences_out_sorted = sorted(sentences_out, key=lambda x: x['index'])
            summary = ' '.join(s['text'] for s in sentences_out_sorted)

            return {'summary': summary, 'sentences': sentences_out_sorted, 'idioma': idioma}

        except Exception as e:
            logger.error(f"Erro ao gerar resumo avançado: {e}", exc_info=True)
            return {'summary': '', 'sentences': []}

    except Exception as e:
        logger.error(f"Erro na pipeline de resumo: {e}", exc_info=True)
        return {'summary': '', 'sentences': []}
