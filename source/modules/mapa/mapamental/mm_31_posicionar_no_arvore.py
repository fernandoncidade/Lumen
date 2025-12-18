from typing import Dict, List
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _posicionar_no_arvore(self, idx: int, filhos: Dict[int, List[int]], larguras: Dict[int, float], x: float, y: float, espacamento_v: float):
    try:
        self.nos[idx].setPos(x, y)
        self._expandir_area_se_necessario(self.nos[idx])

        filhos_no = filhos.get(idx, [])
        if not filhos_no:
            return

        largura_total_filhos = sum(larguras.get(f, 100) for f in filhos_no)
        x_inicio = x - (largura_total_filhos / 2)

        x_atual = x_inicio
        for filho_idx in filhos_no:
            largura_filho = larguras.get(filho_idx, 100)
            x_filho = x_atual + (largura_filho / 2)
            y_filho = y + espacamento_v

            self._posicionar_no_arvore(
                filho_idx, 
                filhos, 
                larguras, 
                x_filho, 
                y_filho, 
                espacamento_v
            )

            x_atual += largura_filho

    except Exception as e:
        logger.error(f"Erro ao posicionar nó na árvore: {e}", exc_info=True)
