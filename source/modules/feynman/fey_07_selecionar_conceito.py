from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def selecionar_conceito(self, item):
    try:
        titulo = item.text().split(' - ')[0].replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')
        conceito = next((c for c in self.conceitos if c['titulo'] == titulo), None)
        if conceito:
            self.conceito_atual = conceito
            self.input_titulo.setPlainText(conceito['titulo'])
            self.texto_explicacao.setPlainText(conceito['explicacao'])
            self.texto_lacunas.setText(conceito['lacunas'])
            self.texto_revisao.setPlainText(conceito['revisao'])
            self.combo_dominio.setCurrentIndex(conceito['dominio'])

    except Exception as e:
        logger.error(f"Erro ao selecionar conceito: {str(e)}", exc_info=True)
