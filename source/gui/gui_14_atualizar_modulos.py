from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def atualizar_modulos(self):
    try:
        if hasattr(self, 'leitor') and hasattr(self.leitor, 'atualizar_traducoes'):
            self.leitor.atualizar_traducoes()

            if hasattr(self.leitor, 'atualizar_fonte_persistente'):
                self.leitor.atualizar_fonte_persistente()

        if hasattr(self, 'gerenciador') and hasattr(self.gerenciador, 'atualizar_traducoes'):
            self.gerenciador.atualizar_traducoes()

        if hasattr(self, 'mapa') and hasattr(self.mapa, 'atualizar_traducoes'):
            self.mapa.atualizar_traducoes()

        if hasattr(self, 'feynman') and hasattr(self.feynman, 'atualizar_traducoes'):
            self.feynman.atualizar_traducoes()

        if hasattr(self, 'eisenhower') and hasattr(self.eisenhower, 'atualizar_textos'):
            self.eisenhower.atualizar_textos()

    except Exception as e:
        logger.error(f"Erro ao atualizar módulos: {str(e)}", exc_info=True)
