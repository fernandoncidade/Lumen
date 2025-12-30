from typing import List, Dict, Any
from source.utils.LogManager import LogManager
import numpy as np

logger = LogManager.get_logger()

def _load_sentence_transformer(self, model_name: str = 'all-MiniLM-L6-v2'):
    try:
        from sentence_transformers import SentenceTransformer
        if getattr(self, '_st_model', None) is None or getattr(self._st_model, 'model_name', None) != model_name:
            self._st_model = SentenceTransformer(model_name)
            try:
                self._st_model.model_name = model_name

            except Exception:
                pass

        return self._st_model

    except Exception as e:
        logger.error(f"Não foi possível carregar SentenceTransformer '{model_name}': {e}", exc_info=True)
        return None


def get_sentence_embeddings(self, texts: List[str], model_name: str = 'all-MiniLM-L6-v2'):
    try:
        model = getattr(self, '_st_model', None)
        if model is None:
            model = _load_sentence_transformer(self, model_name)

        if model is None:
            raise RuntimeError('SentenceTransformer não disponível')

        embs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embs

    except Exception as e:
        logger.error(f"Erro ao obter embeddings: {e}", exc_info=True)
        return np.zeros((len(texts), 1))


def gerar_resumo_semantico(self, caminho_arquivo: str, top_n: int = 5, model_name: str = 'all-MiniLM-L6-v2') -> Dict[str, Any]:
    try:
        texto = self.extrair_texto(caminho_arquivo) if hasattr(self, 'extrair_texto') else None
        if not texto:
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                texto = f.read()

        try:
            doc = self.nlp(texto)
            sents = [s for s in doc.sents if s.text.strip()]
            sent_texts = [s.text.strip() for s in sents]

        except Exception:
            sent_texts = [s.strip() for s in texto.split('.') if s.strip()]
            sents = [type('X', (), {'text': t})() for t in sent_texts]

        if not sent_texts:
            return {'summary': '', 'sentences': []}

        embs = get_sentence_embeddings(self, sent_texts, model_name=model_name)
        if embs is None or len(embs) == 0:
            return {'summary': '', 'sentences': []}

        doc_emb = np.mean(embs, axis=0)
        norms = np.linalg.norm(embs, axis=1) * (np.linalg.norm(doc_emb) + 1e-9)
        sims = np.dot(embs, doc_emb) / (norms + 1e-9)

        idxs = np.argsort(-sims)[:top_n]
        selected = sorted([(int(i), sent_texts[int(i)], float(sims[int(i)])) for i in idxs], key=lambda x: x[0])

        sentences_out = []
        for idx, text, score in selected:
            sentences_out.append({'index': idx, 'text': text, 'score': score})

        summary = ' '.join(s['text'] for s in sentences_out)
        return {'summary': summary, 'sentences': sentences_out}

    except Exception as e:
        logger.error(f"Erro gerar_resumo_semantico: {e}", exc_info=True)
        return {'summary': '', 'sentences': []}
