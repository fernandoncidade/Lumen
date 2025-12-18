from sklearn.feature_extraction.text import TfidfVectorizer
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _gerar_resumo_contextual(self, doc, texto: str, nivel: int, titulo: str, idioma: str) -> str:
    try:
        config_resumo = {
            0: {'num_sentencas': 8, 'max_chars': 1200},  # Documento
            1: {'num_sentencas': 6, 'max_chars': 900},   # Partes
            2: {'num_sentencas': 5, 'max_chars': 700},   # Capítulos
            3: {'num_sentencas': 4, 'max_chars': 500},   # Subcapítulos
            4: {'num_sentencas': 3, 'max_chars': 350},   # Sub-subcapítulos
        }

        cfg = config_resumo.get(nivel, {'num_sentencas': 3, 'max_chars': 350})
        sentencas_list = list(doc.sents)

        if len(sentencas_list) <= cfg['num_sentencas']:
            return texto[:cfg['max_chars']]

        sentencas_scored = []
        textos_sentencas = [sent.text for sent in sentencas_list]

        try:
            vectorizer_local = TfidfVectorizer(
                max_features=50,
                stop_words='english' if idioma == 'en' else None,
                ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer_local.fit_transform(textos_sentencas)

        except:
            tfidf_matrix = None

        for idx, sent in enumerate(sentencas_list):
            sent_texto = sent.text.strip()

            if len(sent_texto) < 20:
                continue

            score = 0.0

            posicao_rel = idx / max(len(sentencas_list) - 1, 1)
            if idx < 3:
                score += 0.35

            elif posicao_rel > 0.8:
                score += 0.25

            else:
                score += 0.1

            if tfidf_matrix is not None:
                tfidf_score = tfidf_matrix[idx].mean()
                score += min(tfidf_score * 3, 0.35)

            comp_ideal = 100
            comp_atual = len(sent_texto)
            if 60 <= comp_atual <= 200:
                score += 0.2

            elif comp_atual < 40 or comp_atual > 300:
                score -= 0.15

            substantivos = [t for t in sent if t.pos_ in ['NOUN', 'PROPN'] and not t.is_stop]
            verbos = [t for t in sent if t.pos_ == 'VERB' and not t.is_stop]

            densidade = (len(substantivos) + len(verbos)) / max(len(sent), 1)
            score += min(densidade * 0.4, 0.25)

            titulo_tokens = set(self.nlp(titulo.lower()))
            titulo_lemmas = {t.lemma_ for t in titulo_tokens if not t.is_stop and len(t.text) > 2}

            sent_lemmas = {t.lemma_ for t in sent if not t.is_stop and len(t.text) > 2}
            overlap = len(titulo_lemmas & sent_lemmas)

            if overlap > 0:
                score += min(overlap * 0.1, 0.3)

            palavras_resumo_pt = {
                'resumindo', 'conclui-se', 'portanto', 'assim', 'dessa forma',
                'principal', 'fundamental', 'essencial', 'importante', 'em suma'
            }

            palavras_resumo_en = {
                'summarizing', 'concluding', 'therefore', 'thus', 'in conclusion',
                'main', 'fundamental', 'essential', 'important', 'in summary'
            }

            palavras_resumo = palavras_resumo_pt | palavras_resumo_en
            sent_lower = sent_texto.lower()

            if any(p in sent_lower for p in palavras_resumo):
                score += 0.25

            sentencas_scored.append({
                'idx': idx,
                'texto': sent_texto,
                'score': score,
                'lemmas': sent_lemmas
            })

        sentencas_scored.sort(key=lambda s: s['score'], reverse=True)
        sentencas_selecionadas = []
        lemmas_ja_usados = set()

        for sent_data in sentencas_scored:
            if len(sentencas_selecionadas) >= cfg['num_sentencas']:
                break

            overlap_atual = len(sent_data['lemmas'] & lemmas_ja_usados)
            taxa_overlap = overlap_atual / max(len(sent_data['lemmas']), 1)

            if taxa_overlap < 0.5 or not sentencas_selecionadas:
                sentencas_selecionadas.append(sent_data)
                lemmas_ja_usados.update(sent_data['lemmas'])

        sentencas_selecionadas.sort(key=lambda s: s['idx'])
        resumo = " ".join([s['texto'] for s in sentencas_selecionadas])

        if len(resumo) > cfg['max_chars']:
            resumo = resumo[:cfg['max_chars']] + "..."

        return resumo

    except Exception as e:
        logger.error(f"Erro ao gerar resumo contextual: {e}", exc_info=True)
        sentencas = [s.text for s in doc.sents][:3]
        return " ".join(sentencas)[:500] + "..."
