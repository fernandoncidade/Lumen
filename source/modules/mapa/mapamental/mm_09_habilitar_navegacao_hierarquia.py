from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _habilitar_navegacao_hierarquia(self, raiz_no):
    try:
        self._modo_navegacao_hierarquia = True
        self._hierarquia_root = raiz_no
        self._nos_expandidos = set()

        self._instalar_handlers_nos()

        for no in self.nos:
            no.setVisible(no == raiz_no)

        self._atualizar_visibilidade_linhas()

        if hasattr(self.view, "animate_focus_on"):
            self.view.animate_focus_on(raiz_no)

    except Exception as e:
        logger.error(f"Erro ao habilitar navegação hierárquica: {e}", exc_info=True)
