import spacy
import fitz
from docx import Document
from typing import List, Dict, Tuple
import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from source.utils.LogManager import LogManager

try:
    from PySide6.QtCore import QCoreApplication

except Exception:
    QCoreApplication = None


class ProcessadorIA:
    def __init__(self):
        self.logger = LogManager.get_logger()
        self.nlp = None
        self.idioma_detectado = 'pt'
        self._carregar_modelo_nlp()

        if QCoreApplication and QCoreApplication.instance():
            self._tr = lambda s: QCoreApplication.translate("App", s)

        else:
            self._tr = lambda s: s

    def _carregar_modelo_nlp(self):
        try:
            try:
                self.nlp = spacy.load("pt_core_news_lg")
                self.idioma_detectado = 'pt'
                self.logger.info("Modelo pt_core_news_lg carregado")

            except OSError:
                try:
                    self.nlp = spacy.load("en_core_web_lg")
                    self.idioma_detectado = 'en'
                    self.logger.info("Modelo en_core_web_lg carregado (fallback)")

                except OSError:
                    self.nlp = spacy.load("pt_core_news_sm")
                    self.idioma_detectado = 'pt'
                    self.logger.warning("Usando modelo pequeno pt_core_news_sm")

            self.nlp.max_length = 2_000_000
            self.logger.info(f"NLP configurado: idioma={self.idioma_detectado}, max_length={self.nlp.max_length}")

        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo spaCy: {e}", exc_info=True)
            raise

    def _detectar_idioma_texto(self, texto: str) -> str:
        palavras_pt = ['capítulo', 'seção', 'introdução', 'conclusão', 'parte', 'português']
        palavras_en = ['chapter', 'section', 'introduction', 'conclusion', 'part', 'english']

        texto_lower = texto.lower()[:5000]

        score_pt = sum(1 for p in palavras_pt if p in texto_lower)
        score_en = sum(1 for p in palavras_en if p in texto_lower)

        return 'pt' if score_pt > score_en else 'en'

    def extrair_texto_pdf(self, caminho: str) -> str:
        try:
            texto = ""
            doc = fitz.open(caminho)
            for pagina in doc:
                texto += pagina.get_text()

            doc.close()
            return texto

        except Exception as e:
            self.logger.error(f"Erro ao extrair texto do PDF: {e}", exc_info=True)
            return ""

    def extrair_texto_docx(self, caminho: str) -> str:
        try:
            doc = Document(caminho)
            texto = "\n".join([paragrafo.text for paragrafo in doc.paragraphs])
            return texto

        except Exception as e:
            self.logger.error(f"Erro ao extrair texto do DOCX: {e}", exc_info=True)
            return ""

    def extrair_texto_txt(self, caminho: str) -> str:
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            self.logger.error(f"Erro ao extrair texto do TXT: {e}", exc_info=True)
            return ""

    def extrair_texto(self, caminho: str) -> str:
        extensao = caminho.lower().split('.')[-1]
        if extensao == 'pdf':
            return self.extrair_texto_pdf(caminho)

        elif extensao == 'docx':
            return self.extrair_texto_docx(caminho)

        elif extensao == 'txt':
            return self.extrair_texto_txt(caminho)

        else:
            raise ValueError(f"Formato não suportado: {extensao}")

    def analisar_estrutura(self, texto: str) -> Dict:
        try:
            self.logger.info("=== INICIANDO ANÁLISE HIERÁRQUICA PROFUNDA ===")

            idioma = self._detectar_idioma_texto(texto)
            self.logger.info(f"Idioma detectado: {idioma}")

            secoes_raw = self._detectar_secoes_avancado(texto, idioma)
            self.logger.info(f"✓ {len(secoes_raw)} seções estruturais detectadas")

            arvore_secoes = self._construir_arvore_hierarquica(texto, secoes_raw)
            self.logger.info("✓ Árvore hierárquica base construída")

            self._processar_hierarquia_completa(texto, arvore_secoes, idioma)
            self.logger.info("✓ Conceitos e ideias principais extraídos")

            self._aplicar_tfidf_global(texto, arvore_secoes)
            self.logger.info("✓ Análise TF-IDF aplicada")

            relacoes_globais = self._identificar_relacoes_semanticas(arvore_secoes)
            arvore_secoes['relacoes'] = relacoes_globais
            self.logger.info(f"✓ {len(relacoes_globais)} relações semânticas identificadas")

            self._log_estrutura_completa(arvore_secoes)

            return arvore_secoes

        except Exception as e:
            self.logger.error(f"Erro ao analisar estrutura: {e}", exc_info=True)
            return {"titulo": "Documento", "conceitos": [], "ideias_principais": [], "relacoes": [], "filhos": []}

    def _detectar_secoes_avancado(self, texto: str, idioma: str = 'pt') -> List[Dict]:
        secoes = []
        linhas = texto.split('\n')

        padroes_pt = [
            {'regex': r'^(?:PARTE|Parte)\s+([IVX\d]+)[\s:.\-]*(.*)$', 'nivel': 1, 'tipo': 'parte'},
            {'regex': r'^(?:CAPÍTULO|Capítulo|CAP\.?)\s+(\d+|[IVX]+)[\s:.\-]*(.*)$', 'nivel': 2, 'tipo': 'capitulo'},
            {'regex': r'^(\d+)\.\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.!?]{5,100})$', 'nivel': 2, 'tipo': 'capitulo_numerado'},
            {'regex': r'^(\d+\.\d+)[\s.\-]+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.!?]{3,100})$', 'nivel': 3, 'tipo': 'subcapitulo'},
            {'regex': r'^(\d+\.\d+\.\d+)[\s.\-]+(.+)$', 'nivel': 4, 'tipo': 'subsubcapitulo'},
        ]

        padroes_en = [
            {'regex': r'^(?:PART|Part)\s+([IVX\d]+)[\s:.\-]*(.*)$', 'nivel': 1, 'tipo': 'parte'},
            {'regex': r'^(?:CHAPTER|Chapter|CHAP\.?)\s+(\d+|[IVX]+)[\s:.\-]*(.*)$', 'nivel': 2, 'tipo': 'capitulo'},
            {'regex': r'^(\d+)\.\s+([A-Z][^.!?]{5,100})$', 'nivel': 2, 'tipo': 'capitulo_numerado'},
            {'regex': r'^(\d+\.\d+)[\s.\-]+([A-Z][^.!?]{3,100})$', 'nivel': 3, 'tipo': 'subcapitulo'},
            {'regex': r'^(\d+\.\d+\.\d+)[\s.\-]+(.+)$', 'nivel': 4, 'tipo': 'subsubcapitulo'},
        ]

        padroes = padroes_pt if idioma == 'pt' else padroes_en

        for i, linha in enumerate(linhas):
            linha_limpa = linha.strip()
            if not linha_limpa or len(linha_limpa) < 3:
                continue

            for padrao in padroes:
                match = re.match(padrao['regex'], linha_limpa, re.IGNORECASE)
                if match:
                    grupos = match.groups()
                    titulo = f"{grupos[0]} {grupos[1]}".strip() if len(grupos) >= 2 else linha_limpa

                    if not re.match(r'^[\d\.\s\-]+$', titulo):
                        secoes.append({
                            'titulo': titulo,
                            'nivel': padrao['nivel'],
                            'posicao': i,
                            'tipo': padrao['tipo']
                        })
                        break

        secoes.sort(key=lambda x: x['posicao'])
        return self._ajustar_niveis_relativos(secoes)

    def _ajustar_niveis_relativos(self, secoes: List[Dict]) -> List[Dict]:
        if not secoes:
            return secoes

        nivel_min = min(s['nivel'] for s in secoes)

        for secao in secoes:
            secao['nivel'] = secao['nivel'] - nivel_min + 1

        return secoes

    def _construir_arvore_hierarquica(self, texto: str, secoes_raw: List[Dict]) -> Dict:
        try:
            linhas = texto.split('\n')

            raiz = {
                'titulo': self._tr('Documento Principal'),
                'nivel': 0,
                'posicao_inicio': 0,
                'posicao_fim': len(linhas),
                'texto_puro': '',
                'conceitos': [],
                'ideias_principais': [],
                'filhos': [],
                'tipo': 'raiz'
            }

            if not secoes_raw:
                raiz['texto_puro'] = texto
                return raiz

            nos_secoes = []
            for i, secao in enumerate(secoes_raw):
                inicio = secao['posicao']
                fim = len(linhas)

                for j in range(i + 1, len(secoes_raw)):
                    if secoes_raw[j]['nivel'] <= secao['nivel']:
                        fim = secoes_raw[j]['posicao']
                        break

                texto_puro = '\n'.join(linhas[inicio+1:fim]).strip()

                no = {
                    'titulo': secao['titulo'],
                    'nivel': secao['nivel'],
                    'posicao_inicio': inicio,
                    'posicao_fim': fim,
                    'texto_puro': texto_puro,
                    'conceitos': [],
                    'ideias_principais': [],
                    'filhos': [],
                    'tipo': secao.get('tipo', 'secao')
                }
                nos_secoes.append(no)

            stack = [raiz]
            for no in nos_secoes:
                nivel_no = no['nivel']
                while len(stack) > 1 and stack[-1]['nivel'] >= nivel_no:
                    stack.pop()

                pai = stack[-1]
                pai['filhos'].append(no)
                stack.append(no)

            if nos_secoes:
                raiz['texto_puro'] = '\n'.join(linhas[:nos_secoes[0]['posicao_inicio']])

            else:
                raiz['texto_puro'] = texto

            return raiz

        except Exception as e:
            self.logger.error(f"Erro ao construir árvore: {e}", exc_info=True)
            return raiz

    def _processar_hierarquia_completa(self, texto_completo: str, no: Dict, idioma: str):
        try:
            texto_puro = no.get('texto_puro', '').strip()
            nivel = no.get('nivel', 0)
            titulo = no.get('titulo', 'Nó')

            if texto_puro and len(texto_puro) > 50:
                doc_no = self.nlp(texto_puro[:1_000_000])

                conceitos = self._extrair_conceitos_semanticos(doc_no, texto_puro, nivel)
                no['conceitos'] = conceitos

                ideias = self._extrair_ideias_principais(doc_no, texto_puro, nivel)
                no['ideias_principais'] = ideias

                resumo = self._gerar_resumo_contextual(doc_no, texto_puro, nivel, titulo, idioma)
                no['resumo_contextual'] = resumo

                self.logger.info(
                    f"✓ '{titulo[:40]}' (nível {nivel}): "
                    f"{len(conceitos)} conceitos + {len(ideias)} ideias + resumo ({len(resumo)} chars)"
                )

            else:
                no['conceitos'] = []
                no['ideias_principais'] = []
                no['resumo_contextual'] = ""

            for filho in no.get('filhos', []):
                self._processar_hierarquia_completa(texto_completo, filho, idioma)

        except Exception as e:
            self.logger.error(f"Erro ao processar nó: {e}", exc_info=True)

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
            self.logger.error(f"Erro ao gerar resumo contextual: {e}", exc_info=True)
            sentencas = [s.text for s in doc.sents][:3]
            return " ".join(sentencas)[:500] + "..."

    def _extrair_conceitos_semanticos(self, doc, texto: str, nivel: int) -> List[Dict]:
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

    def _extrair_ideias_principais(self, doc, texto: str, nivel: int) -> List[Dict]:
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
            self.logger.info("✓ TF-IDF aplicado para refinar importâncias")

        except Exception as e:
            self.logger.error(f"Erro ao aplicar TF-IDF: {e}", exc_info=True)

    def _identificar_relacoes_semanticas(self, arvore: Dict) -> List[Tuple[str, str, str]]:
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

    def _log_estrutura_completa(self, no: Dict, nivel: int = 0):
        try:
            indent = "  " * nivel
            titulo = no.get('titulo', self._tr('Sem título'))[:50]
            num_conceitos = len(no.get('conceitos', []))
            num_ideias = len(no.get('ideias_principais', []))
            num_filhos = len(no.get('filhos', []))

            simbolo = {0: "🌳", 1: "🌿", 2: "🌱", 3: "🍃", 4: "🌾"}.get(nivel, "•")

            self.logger.debug(
                f"{indent}{simbolo} [{nivel}] {titulo} "
                f"({num_conceitos} conceitos, {num_ideias} ideias, {num_filhos} filhos)"
            )

            for filho in no.get('filhos', []):
                self._log_estrutura_completa(filho, nivel + 1)

        except Exception as e:
            self.logger.error(f"Erro ao logar estrutura: {e}")

    def _extrair_conceitos_tfidf(self, doc, texto: str, max_conceitos: int = 15) -> List[Dict]:
        try:
            sentencas = [s.text.strip() for s in doc.sents if s.text.strip()]
            if not sentencas:
                sentencas = [texto]

            vectorizer = TfidfVectorizer(
                max_features=300,
                stop_words='english' if self.idioma_detectado == 'en' else None,
                ngram_range=(1, 3)
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

            noun_chunks = set([nc.text.strip().lower() for nc in doc.noun_chunks if len(nc) <= 6])

            for termo, score in termos_scores[:max_conceitos * 2]:
                t = termo.strip()
                if len(t) < 3 or t in usados:
                    continue

                tipo = 'termo_tecnico' if t in noun_chunks or len(t.split()) >= 2 else 'conceito'
                ctx = contexto_para(t)
                frequencia = sum(s.lower().count(t.lower()) for s in sentencas)
                importancia = min(0.4 + score * 0.8 + (0.05 if tipo == 'termo_tecnico' else 0), 1.0)

                conceitos.append({
                    'texto': t,
                    'tipo': tipo,
                    'importancia': float(importancia),
                    'frequencia': int(frequencia),
                    'contextos': ctx
                })
                usados.add(t)

                if len(conceitos) >= max_conceitos:
                    break

            if not conceitos:
                conceitos = self._extrair_conceitos_semanticos(doc, texto, nivel=0)

            return conceitos

        except Exception as e:
            self.logger.error(f"Erro em _extrair_conceitos_tfidf: {e}", exc_info=True)
            return []

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
            self.logger.error(f"Erro em _identificar_relacoes_avancadas: {e}", exc_info=True)
            return []
