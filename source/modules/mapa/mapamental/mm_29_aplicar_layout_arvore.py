from typing import Dict
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_03_MapaMental import MapaScene

logger = LogManager.get_logger()

def _aplicar_layout_arvore(self, hierarquia: Dict):
    try:
        if not hierarquia or 'raiz' not in hierarquia:
            return

        raiz_idx = hierarquia['raiz']
        filhos = hierarquia['filhos']
        niveis = hierarquia['niveis']

        ESPACAMENTO_VERTICAL = 150
        ESPACAMENTO_HORIZONTAL_BASE = 200

        nos_por_nivel = {}
        for idx, nivel in niveis.items():
            if nivel not in nos_por_nivel:
                nos_por_nivel[nivel] = []

            nos_por_nivel[nivel].append(idx)

        larguras = self._calcular_larguras_subarvore(raiz_idx, filhos, ESPACAMENTO_HORIZONTAL_BASE)
        self._posicionar_no_arvore(raiz_idx, filhos, larguras, x=0, y=0, espacamento_v=ESPACAMENTO_VERTICAL)

        if isinstance(self.scene, MapaScene):
            for no in self.nos:
                pos = self.scene.snap(no.scenePos())
                no.setPos(pos)

    except Exception as e:
        logger.error(f"Erro ao aplicar layout em árvore: {e}", exc_info=True)
