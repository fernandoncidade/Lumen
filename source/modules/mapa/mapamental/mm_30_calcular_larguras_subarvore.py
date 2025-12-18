from typing import Dict, List
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _calcular_larguras_subarvore(self, idx: int, filhos: Dict[int, List[int]], espacamento_base: float) -> Dict[int, float]:
    try:
        larguras = {}

        def calcular_recursivo(no_idx: int) -> float:
            filhos_no = filhos.get(no_idx, [])

            if not filhos_no:
                larguras[no_idx] = espacamento_base
                return espacamento_base

            largura_total = sum(calcular_recursivo(f) for f in filhos_no)
            larguras[no_idx] = max(largura_total, espacamento_base)
            return larguras[no_idx]

        calcular_recursivo(idx)
        return larguras

    except Exception as e:
        logger.error(f"Erro ao calcular larguras de subárvore: {e}", exc_info=True)
        return {}
