from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _aplicar_visibilidade_por_foco(self, foco, abrir_foco: bool):
    try:
        if not self._hierarquia_root:
            return

        vis_antes = {n for n in (getattr(self, "nos", []) or []) if getattr(n, "isVisible", lambda: True)()}

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

        orient = str(getattr(self, "_lumen_layout_orientation", "free") or "free").lower()
        if orient in ("vertical", "horizontal"):
            try:
                freeze = bool(getattr(self, "_lumen_layout_freeze_on_click", False))
                if freeze:
                    vis_depois = {n for n in (getattr(self, "nos", []) or []) if getattr(n, "isVisible", lambda: True)()}
                    novos = set(vis_depois - vis_antes)
                    removidos = set(vis_antes - vis_depois)
                    fixos = set(vis_antes & vis_depois)

                    from source.modules.mapa.mapamental.mm_34_layout_hierarquia_navegacao import (_layout_incremental_preservando_base,)
                    _layout_incremental_preservando_base(self, novos_visiveis=novos, fixos_visiveis=fixos, removidos_visiveis=removidos)

                else:
                    from source.modules.mapa.mapamental.mm_34_layout_hierarquia_navegacao import (_layout_hierarquia_navegacao,)
                    _layout_hierarquia_navegacao(self)

            except Exception:
                pass

    except Exception as e:
        logger.error(f"Erro ao aplicar visibilidade por foco: {e}", exc_info=True)
