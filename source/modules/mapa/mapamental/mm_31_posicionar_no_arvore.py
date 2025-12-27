from typing import Dict, List
from source.utils.LogManager import LogManager
from PySide6.QtCore import QRectF

logger = LogManager.get_logger()

def _posicionar_no_arvore(self, idx: int, filhos: Dict[int, List[int]], larguras: Dict[int, float], x: float, y: float, espacamento_v: float):
    try:
        nos = getattr(self, "nos", []) or []
        if not (0 <= idx < len(nos)):
            return

        self.nos[idx].setPos(x, y)
        self._expandir_area_se_necessario(self.nos[idx])

        filhos_no = filhos.get(idx, []) or []
        try:
            filhos_no = [f for f in filhos_no if 0 <= f < len(nos) and getattr(nos[f], "isVisible", lambda: True)()]

        except Exception:
            pass

        if not filhos_no:
            return

        largura_total_filhos = sum(larguras.get(f,  max(200.0, espacamento_v)) for f in filhos_no)
        GAP_MIN = max(espacamento_v * 0.1, 20.0)
        largura_total_filhos += GAP_MIN * max(0, (len(filhos_no)-1))

        x_inicio = x - (largura_total_filhos / 2.0)

        alturas = []
        for f in filhos_no:
            try:
                r: QRectF = nos[f].mapToScene(nos[f].boundingRect()).boundingRect()
                alturas.append(r.height())

            except Exception:
                alturas.append(80.0)

        max_h = max(alturas) if alturas else 80.0
        espacamento_real_v = max(espacamento_v, max_h * 1.4)

        x_atual = x_inicio
        for i, filho_idx in enumerate(filhos_no):
            largura_filho = larguras.get(filho_idx, max(200.0, espacamento_v))
            x_filho = x_atual + (largura_filho / 2.0)
            y_filho = y + espacamento_real_v

            try:
                self._posicionar_no_arvore(
                    filho_idx,
                    filhos,
                    larguras,
                    x_filho,
                    y_filho,
                    espacamento_v
                )

            except Exception as e:
                logger.error(f"Erro ao posicionar subnó {filho_idx}: {e}", exc_info=True)

            x_atual += largura_filho + GAP_MIN

    except Exception as e:
        logger.error(f"Erro ao posicionar nó na árvore: {e}", exc_info=True)
