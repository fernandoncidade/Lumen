from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def limpar_campos(self):
    try:
        self.input_titulo.clear()
        self.texto_explicacao.clear()
        self.texto_lacunas.clear()
        self.texto_revisao.clear()
        self.combo_dominio.setCurrentIndex(0)

    except Exception as e:
        logger.error(f"Erro ao limpar campos: {str(e)}", exc_info=True)
