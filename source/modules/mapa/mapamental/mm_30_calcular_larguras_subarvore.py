from typing import Dict, List, Set
from source.utils.LogManager import LogManager
from PySide6.QtCore import QRectF

logger = LogManager.get_logger()

def _calcular_larguras_subarvore(self, idx: int, filhos: Dict[int, List[int]], espacamento_base: float, visiveis: Set[int] | None = None) -> Dict[int, float]:
    try:
        nos = getattr(self, "nos", []) or []
        H_MARGIN = 40.0
        GAP_INTER_FILHOS = max(espacamento_base * 0.1, 20.0)

        def _rect_scene_width(i: int) -> float:
            try:
                no = nos[i]
                r: QRectF = no.mapToScene(no.boundingRect()).boundingRect()
                return max(r.width(), espacamento_base) + H_MARGIN

            except Exception:
                return espacamento_base + H_MARGIN

        larguras: Dict[int, float] = {}

        visited = set()

        def calcular_rec(no_idx: int) -> float:
            if no_idx in visited:
                return larguras.get(no_idx, espacamento_base)

            visited.add(no_idx)

            filhos_no = (filhos.get(no_idx, []) or [])
            if visiveis is not None:
                filhos_no = [f for f in filhos_no if f in visiveis]

            if not filhos_no:
                w = _rect_scene_width(no_idx)
                larguras[no_idx] = max(w, espacamento_base)
                return larguras[no_idx]

            soma_filhos = 0.0
            for f in filhos_no:
                wf = calcular_rec(f)
                soma_filhos += wf

            soma_filhos += max(0, (len(filhos_no) - 1)) * GAP_INTER_FILHOS
            own_w = _rect_scene_width(no_idx)
            larguras[no_idx] = max(own_w, soma_filhos, espacamento_base)
            return larguras[no_idx]

        calcular_rec(idx)
        return larguras

    except Exception as e:
        logger.error(f"Erro ao calcular larguras de subárvore: {e}", exc_info=True)
        return {}
