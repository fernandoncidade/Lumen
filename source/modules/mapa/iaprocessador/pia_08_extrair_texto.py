from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def extrair_texto(self, caminho: str) -> str:
    try:
        extensao = caminho.lower().split('.')[-1]
        if extensao == 'pdf':
            return self.extrair_texto_pdf(caminho)

        elif extensao == 'docx':
            return self.extrair_texto_docx(caminho)

        elif extensao == 'txt':
            return self.extrair_texto_txt(caminho)

        else:
            raise ValueError(f"Formato não suportado: {extensao}")

    except Exception as e:
        logger.error(f"Erro ao extrair texto do arquivo: {e}", exc_info=True)
        return ""
