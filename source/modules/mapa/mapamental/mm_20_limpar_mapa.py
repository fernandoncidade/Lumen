from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def limpar_mapa(self):
    try:
        self.scene.clear()
        self.nos.clear()
        self.no_origem = None

        self._modo_navegacao_hierarquia = False
        self._hierarquia_root = None
        self._hierarquia_parent = {}
        self._hierarquia_children = {}
        self._nos_expandidos = set()

    except Exception as e:
        logger.error(f"Erro ao limpar mapa: {str(e)}", exc_info=True)
