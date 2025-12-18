from typing import Dict, List
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao

logger = LogManager.get_logger()

def _obter_conexoes_existentes(self) -> Dict[int, List[int]]:
    try:
        conexoes = {i: [] for i in range(len(self.nos))}

        for item in self.scene.items():
            if isinstance(item, LinhaConexao):
                try:
                    idx_inicio = self.nos.index(item.no_inicio)
                    idx_fim = self.nos.index(item.no_fim)
                    conexoes[idx_inicio].append(idx_fim)
                    conexoes[idx_fim].append(idx_inicio)

                except ValueError:
                    continue

        return conexoes

    except Exception as e:
        logger.error(f"Erro ao obter conexões existentes: {e}", exc_info=True)
        return {}
