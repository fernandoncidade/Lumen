from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _aplicar_visibilidade_por_foco(self, foco, abrir_foco: bool):
    try:
        if not self._hierarquia_root:
            return

        visiveis = set()
        visiveis.add(self._hierarquia_root)

        for no_exp in self._nos_expandidos:
            if no_exp not in visiveis:
                n = no_exp
                while n is not None:
                    visiveis.add(n)
                    n = self._hierarquia_parent.get(n)

            for filho in self._hierarquia_children.get(no_exp, []):
                visiveis.add(filho)

        for no in self.nos:
            no.setVisible(no in visiveis)

        self._atualizar_visibilidade_linhas()

    except Exception as e:
        logger.error(f"Erro ao aplicar visibilidade por foco: {e}", exc_info=True)
