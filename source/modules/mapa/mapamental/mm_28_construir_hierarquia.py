from typing import Dict, List
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _construir_hierarquia(self, conexoes: Dict[int, List[int]]) -> Dict:
    try:
        if not self.nos:
            return {}

        contagem_conexoes = [(i, len(conns)) for i, conns in conexoes.items()]
        contagem_conexoes.sort(key=lambda x: x[1], reverse=True)

        raiz_idx = contagem_conexoes[0][0] if contagem_conexoes else 0

        visitados = set()
        niveis = {raiz_idx: 0}
        filhos = {i: [] for i in range(len(self.nos))}
        pais = {i: None for i in range(len(self.nos))}

        fila = [raiz_idx]
        visitados.add(raiz_idx)

        while fila:
            atual = fila.pop(0)
            nivel_atual = niveis[atual]

            for vizinho in conexoes[atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    niveis[vizinho] = nivel_atual + 1
                    filhos[atual].append(vizinho)
                    pais[vizinho] = atual
                    fila.append(vizinho)

        for i in range(len(self.nos)):
            if i not in visitados:
                visitados.add(i)
                niveis[i] = 1
                filhos[raiz_idx].append(i)
                pais[i] = raiz_idx

        return {
            'raiz': raiz_idx,
            'niveis': niveis,
            'filhos': filhos,
            'pais': pais
        }

    except Exception as e:
        logger.error(f"Erro ao construir hierarquia: {e}", exc_info=True)
        return {}
