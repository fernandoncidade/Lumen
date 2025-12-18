from source.utils.LogManager import LogManager
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao

logger = LogManager.get_logger()

def _atualizar_visibilidade_linhas(self):
    try:
        for item in self.scene.items():
            if isinstance(item, LinhaConexao):
                a = getattr(item, "no_inicio", None)
                b = getattr(item, "no_fim", None)
                if a is None or b is None:
                    item.setVisible(True)
                    continue

                item.setVisible(a.isVisible() and b.isVisible())

    except Exception as e:
        logger.error(f"Erro ao atualizar visibilidade das linhas: {e}", exc_info=True)
