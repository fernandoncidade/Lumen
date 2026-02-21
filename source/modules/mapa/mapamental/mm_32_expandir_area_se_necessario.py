from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _expandir_area_se_necessario(self, no):
    try:
        margem = 1000
        pos = no.scenePos()
        rect_atual = self.scene.sceneRect()

        precisa_expandir = False
        novo_left = rect_atual.left()
        novo_top = rect_atual.top()
        novo_right = rect_atual.right()
        novo_bottom = rect_atual.bottom()

        if pos.x() < rect_atual.left() + margem:
            novo_left = pos.x() - margem * 2
            precisa_expandir = True

        if pos.x() > rect_atual.right() - margem:
            novo_right = pos.x() + margem * 2
            precisa_expandir = True

        if pos.y() < rect_atual.top() + margem:
            novo_top = pos.y() - margem * 2
            precisa_expandir = True

        if pos.y() > rect_atual.bottom() - margem:
            novo_bottom = pos.y() + margem * 2
            precisa_expandir = True

        if precisa_expandir:
            nova_largura = novo_right - novo_left
            nova_altura = novo_bottom - novo_top
            self.scene.setSceneRect(novo_left, novo_top, nova_largura, nova_altura)
            logger.debug(
                f"Área expandida para: x={novo_left:.0f}, y={novo_top:.0f}, "
                f"w={nova_largura:.0f}, h={nova_altura:.0f}"
            )

    except Exception as e:
        logger.error(f"Erro ao expandir área: {str(e)}", exc_info=True)
