from typing import List, Dict
from collections import defaultdict
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _extrair_conceitos_semanticos(self, doc, texto: str, nivel: int) -> List[Dict]:
    try:
        conceitos: List[Dict] = []

        def _sentencas(doc_):
            try:
                sents = list(doc_.sents)
                return sents if sents else [doc_]

            except Exception:
                return [doc_]

        def _tem_parser(doc_):
            try:
                if getattr(doc_, "is_parsed", False):
                    return True

                if hasattr(doc_, "has_annotation"):
                    return bool(doc_.has_annotation("DEP"))

            except Exception:
                pass

            return False

        entidades = defaultdict(list)
        try:
            for ent in getattr(doc, "ents", []) or []:
                if ent.label_ in ["PER", "ORG", "LOC", "MISC", "EVENT", "PERSON", "GPE", "NORP"]:
                    entidades[ent.text.lower()].append(ent.sent.text.strip() if hasattr(ent, "sent") else ent.text)

        except Exception:
            entidades = defaultdict(list)

        for texto_ent, contextos in entidades.items():
            conceitos.append({
                "texto": texto_ent.title(),
                "tipo": "entidade",
                "importancia": min(0.9, 0.7 + len(contextos) * 0.03),
                "frequencia": len(contextos),
                "contextos": contextos[:5],
            })

        termos = defaultdict(lambda: {"freq": 0, "contextos": []})

        if _tem_parser(doc):
            try:
                for chunk in doc.noun_chunks:
                    if 2 <= len(chunk) <= 5:
                        termo_texto = chunk.text.strip()
                        termos[termo_texto]["freq"] += 1
                        termos[termo_texto]["contextos"].append(chunk.sent.text.strip())

            except Exception as e:
                logger.warning(f"noun_chunks indisponível; usando heurística. Detalhe: {e}")

        else:
            for sent in _sentencas(doc):
                try:
                    toks = [
                        t for t in sent
                        if getattr(t, "is_alpha", False)
                        and not getattr(t, "is_stop", False)
                        and len(getattr(t, "text", "")) > 2
                    ]
                    words = []
                    for t in toks:
                        lemma = getattr(t, "lemma_", "") or getattr(t, "text", "")
                        words.append(lemma.lower())

                    for n in (2, 3, 4):
                        for i in range(0, max(len(words) - n + 1, 0)):
                            frase = " ".join(words[i:i+n]).strip()
                            if len(frase) < 6:
                                continue

                            termos[frase]["freq"] += 1
                            if len(termos[frase]["contextos"]) < 5:
                                termos[frase]["contextos"].append(getattr(sent, "text", "")[:350].strip())

                except Exception:
                    continue

        for termo, dados in termos.items():
            if dados["freq"] >= 2:
                importancia = 0.5 + (len(termo.split()) * 0.08) + (min(dados["freq"], 10) * 0.03)
                conceitos.append({
                    "texto": termo,
                    "tipo": "termo_tecnico",
                    "importancia": min(importancia, 0.95),
                    "frequencia": int(dados["freq"]),
                    "contextos": dados["contextos"][:5],
                })

        subst = defaultdict(list)
        for sent in _sentencas(doc):
            for token in sent:
                try:
                    if not getattr(token, "is_alpha", False):
                        continue

                    if getattr(token, "is_stop", False):
                        continue

                    if len(getattr(token, "text", "")) <= 3:
                        continue

                    pos = getattr(token, "pos_", "") or ""
                    lemma = (getattr(token, "lemma_", "") or getattr(token, "text", "")).lower()

                    if pos in ("NOUN", "PROPN") or (pos in ("", "X") and not getattr(self, "_nlp_modo_reduzido", False)):
                        subst[lemma].append(getattr(sent, "text", "")[:350].strip())

                    elif getattr(self, "_nlp_modo_reduzido", False):
                        subst[lemma].append(getattr(sent, "text", "")[:350].strip())

                except Exception:
                    continue

        for lemma, contextos in subst.items():
            if len(contextos) >= 3:
                conceitos.append({
                    "texto": lemma.capitalize(),
                    "tipo": "conceito",
                    "importancia": min(0.7, 0.4 + len(contextos) * 0.04),
                    "frequencia": len(contextos),
                    "contextos": contextos[:5],
                })

        conceitos = sorted(conceitos, key=lambda c: c.get("importancia", 0.0), reverse=True)
        limite = {0: 12, 1: 10, 2: 8, 3: 6, 4: 5}.get(nivel, 5)
        return conceitos[:limite]

    except Exception as e:
        logger.error(f"Erro ao extrair conceitos semânticos: {e}", exc_info=True)
        return []
