from typing import List, Tuple
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao

logger = LogManager.get_logger()

def _criar_relacoes_ia(self, relacoes: List[Tuple]):
    try:
        mapa_nos = {no.texto.lower(): no for no in self.nos}

        for sujeito, verbo, objeto in relacoes[:20]:
            no_origem = mapa_nos.get(sujeito)
            no_destino = mapa_nos.get(objeto)

            if no_origem and no_destino and no_origem != no_destino:
                ja_conectado = any(
                    (linha.no_inicio == no_origem and linha.no_fim == no_destino) or
                    (linha.no_inicio == no_destino and linha.no_fim == no_origem)
                    for linha in self.scene.items() if isinstance(linha, LinhaConexao)
                )

                if not ja_conectado:
                    linha = LinhaConexao(no_origem, no_destino)
                    self.scene.addItem(linha)

    except Exception as e:
        logger.error(f"Erro ao criar relações: {str(e)}", exc_info=True)
