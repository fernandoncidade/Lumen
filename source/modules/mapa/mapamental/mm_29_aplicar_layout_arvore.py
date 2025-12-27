from typing import Dict, Optional, Set
from PySide6.QtCore import QPointF
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _aplicar_layout_arvore(self, hierarquia: Dict, orientacao: str = "vertical", espacamento_vertical: int | None = None, espacamento_horizontal_base: int | None = None, visiveis: Optional[Set[int]] = None):
    try:
        if not hierarquia or 'raiz' not in hierarquia:
            return

        raiz_idx = hierarquia['raiz']
        filhos = hierarquia['filhos']
        niveis = hierarquia['niveis']

        ESPACAMENTO_VERTICAL = int(espacamento_vertical) if espacamento_vertical is not None else 150
        ESPACAMENTO_HORIZONTAL_BASE = int(espacamento_horizontal_base) if espacamento_horizontal_base is not None else 200

        nos_por_nivel = {}
        for idx, nivel in niveis.items():
            nos_por_nivel.setdefault(nivel, []).append(idx)

        if visiveis is None:
            visiveis_idx = {i for i, no in enumerate(getattr(self, "nos", []) or []) if getattr(no, "isVisible", lambda: True)()}

        else:
            visiveis_idx = set(visiveis)

        larguras = self._calcular_larguras_subarvore(raiz_idx, filhos, ESPACAMENTO_HORIZONTAL_BASE, visiveis=visiveis_idx)
        self._posicionar_no_arvore(raiz_idx, filhos, larguras, x=0, y=0, espacamento_v=ESPACAMENTO_VERTICAL)

        if orientacao == "horizontal":
            try:
                raiz_no = self.nos[raiz_idx] if 0 <= raiz_idx < len(self.nos) else None
                ancora = raiz_no.pos() if raiz_no is not None else QPointF(0, 0)

                for no in (getattr(self, "nos", []) or []):
                    p = no.pos() - ancora
                    no.setPos(QPointF(p.y(), p.x()) + ancora)

            except Exception as e:
                logger.error(f"Erro ao rotacionar layout para orientação horizontal: {e}", exc_info=True)

        try:
            sc = getattr(self, "scene", None)
            if sc is not None and hasattr(sc, "snap"):
                for no in getattr(self, "nos", []) or []:
                    no.setPos(sc.snap(no.scenePos()))

        except Exception:
            pass

        try:
            from source.modules.mapa.mapamental.mm_34_layout_hierarquia_navegacao import _resolver_sobreposicoes_global

            if orientacao == "horizontal":
                _resolver_sobreposicoes_global(self, nos=getattr(self, "nos", []) or [], apenas_visiveis=True, push_direcao="right")
                _resolver_sobreposicoes_global(self, nos=getattr(self, "nos", []) or [], apenas_visiveis=True, push_direcao="down")

            else:
                _resolver_sobreposicoes_global(self, nos=getattr(self, "nos", []) or [], apenas_visiveis=True, push_direcao="down")

        except Exception:
            pass

        try:
            br = self.scene.itemsBoundingRect()
            if not br.isNull() and not br.isEmpty():
                padding = 1400
                alvo = br.adjusted(-padding, -padding, padding, padding)
                atual = self.scene.sceneRect()
                self.scene.setSceneRect(alvo if (atual.isNull() or atual.isEmpty()) else atual.united(alvo))

        except Exception as e:
            logger.error(f"Erro ao ajustar sceneRect pós-layout: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao aplicar layout em árvore: {e}", exc_info=True)
