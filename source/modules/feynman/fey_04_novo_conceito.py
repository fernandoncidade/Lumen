from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def novo_conceito(self):
    try:
        self.conceito_atual = {
            'titulo': '',
            'explicacao': '',
            'lacunas': '',
            'revisao': '',
            'dominio': 0
        }
        self.limpar_campos()

    except Exception as e:
        logger.error(f"Erro ao criar novo conceito: {str(e)}", exc_info=True)
