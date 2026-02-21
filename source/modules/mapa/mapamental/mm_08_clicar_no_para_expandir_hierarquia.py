from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _clicar_no_para_expandir_hierarquia(self, no):
    try:
        if no in self._nos_expandidos:
            self._nos_expandidos.discard(no)

            def remover_descendentes(n):
                for filho in self._hierarquia_children.get(n, []):
                    self._nos_expandidos.discard(filho)
                    remover_descendentes(filho)

            remover_descendentes(no)

        else:
            self._nos_expandidos.add(no)

        self._aplicar_visibilidade_por_foco(no, abrir_foco=False)

    except Exception as e:
        logger.error(f"Erro ao expandir/recolher hierarquia: {e}", exc_info=True)
