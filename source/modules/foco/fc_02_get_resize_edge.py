from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def get_resize_edge(self, pos):
    try:
        margin = self.resize_margin
        rect = self.rect()

        left = pos.x() < margin
        right = pos.x() > rect.width() - margin
        top = pos.y() < margin
        bottom = pos.y() > rect.height() - margin

        if top and left:
            return 'top-left'

        elif top and right:
            return 'top-right'

        elif bottom and left:
            return 'bottom-left'

        elif bottom and right:
            return 'bottom-right'

        elif left:
            return 'left'

        elif right:
            return 'right'

        elif top:
            return 'top'

        elif bottom:
            return 'bottom'

        return None

    except Exception as e:
        logger.error(f"Erro ao determinar borda de redimensionamento: {str(e)}", exc_info=True)
        return None
