from typing import Dict
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _configurar_hierarquia_por_indices(self, hierarquia: Dict):
    try:
        if not hierarquia or "raiz" not in hierarquia:
            return

        raiz_idx = hierarquia["raiz"]
        pais_idx = hierarquia.get("pais", {})
        filhos_idx = hierarquia.get("filhos", {})

        if not (0 <= raiz_idx < len(self.nos)):
            return

        self._hierarquia_parent = {}
        self._hierarquia_children = {}

        raiz = self.nos[raiz_idx]
        self._hierarquia_parent[raiz] = None
        self._hierarquia_children.setdefault(raiz, [])

        for pai_i, lista_filhos in filhos_idx.items():
            if not (0 <= pai_i < len(self.nos)):
                continue

            pai_no = self.nos[pai_i]
            self._hierarquia_children.setdefault(pai_no, [])

            for fi in lista_filhos:
                if not (0 <= fi < len(self.nos)):
                    continue

                filho_no = self.nos[fi]
                self._hierarquia_parent[filho_no] = pai_no
                self._hierarquia_children[pai_no].append(filho_no)
                self._hierarquia_children.setdefault(filho_no, [])

        self._habilitar_navegacao_hierarquia(raiz)

    except Exception as e:
        logger.error(f"Erro ao configurar hierarquia por índices: {e}", exc_info=True)
