from typing import List, Dict
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _construir_arvore_hierarquica(self, texto: str, secoes_raw: List[Dict]) -> Dict:
    linhas = (texto or "").split("\n")
    def _extrair_titulo_documento(texto: str, secoes: List[Dict]) -> str:
        try:
            if secoes:
                for s in secoes:
                    pos = s.get('posicao', 0)
                    if int(pos) <= 2:
                        t = s.get('titulo', '').strip()
                        if t:
                            return t

            linhas_topo = [ln.strip() for ln in (texto or "").split('\n')[:12] if ln.strip()]
            if linhas_topo:
                for ln in linhas_topo:
                    if 3 < len(ln) < 200 and not ln.endswith(('.', '?', '!')):
                        low = ln.lower()
                        if any(k in low for k in ['sumário', 'sumario', 'índice', 'indice', 'capítulo', 'chapter', 'prefácio', 'prefacio']):
                            continue

                        return ln

            if linhas_topo:
                return linhas_topo[0]

        except Exception:
            pass

        return "Documento Principal"

    titulo_raiz_key = _extrair_titulo_documento(texto, secoes_raw)

    raiz = {
        "titulo": titulo_raiz_key,
        "titulo_key": titulo_raiz_key,
        "nivel": 0,
        "posicao_inicio": 0,
        "posicao_fim": len(linhas),
        "texto_puro": texto or "",
        "conceitos": [],
        "ideias_principais": [],
        "filhos": [],
        "tipo": "raiz",
    }

    try:
        if not secoes_raw:
            return raiz

        nos_secoes = []
        for i, secao in enumerate(secoes_raw):
            inicio = secao["posicao"]
            fim = len(linhas)

            for j in range(i + 1, len(secoes_raw)):
                if secoes_raw[j]["nivel"] <= secao["nivel"]:
                    fim = secoes_raw[j]["posicao"]
                    break

            texto_puro = "\n".join(linhas[inicio + 1 : fim]).strip()

            no = {
                "titulo": secao["titulo"],
                "nivel": secao["nivel"],
                "posicao_inicio": inicio,
                "posicao_fim": fim,
                "texto_puro": texto_puro,
                "conceitos": [],
                "ideias_principais": [],
                "filhos": [],
                "tipo": secao.get("tipo", "secao"),
            }
            nos_secoes.append(no)

        stack = [raiz]
        for no in nos_secoes:
            nivel_no = no["nivel"]
            while len(stack) > 1 and stack[-1]["nivel"] >= nivel_no:
                stack.pop()

            pai = stack[-1]
            pai["filhos"].append(no)
            stack.append(no)

        return raiz

    except Exception as e:
        logger.error(f"Erro ao construir árvore: {e}", exc_info=True)
        return raiz
