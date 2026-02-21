from typing import List, Dict
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _ajustar_niveis_relativos(self, secoes: List[Dict]) -> List[Dict]:
    try:
        if not secoes:
            return secoes

        nivel_minimo = min(s['nivel'] for s in secoes)
        for secao in secoes:
            secao['nivel'] = secao['nivel'] - nivel_minimo + 1

        niveis_ajustados = []
        nivel_anterior = 0

        for secao in secoes:
            nivel_atual = secao['nivel']

            if nivel_atual > nivel_anterior + 1:
                secao['nivel'] = nivel_anterior + 1
                logger.debug(
                    f"Ajustando nível de '{secao['titulo'][:30]}' "
                    f"de {nivel_atual} para {secao['nivel']}"
                )

            nivel_anterior = secao['nivel']
            niveis_ajustados.append(secao)

        return niveis_ajustados

    except Exception as e:
        logger.error(f"Erro ao ajustar níveis: {e}", exc_info=True)
        return secoes
