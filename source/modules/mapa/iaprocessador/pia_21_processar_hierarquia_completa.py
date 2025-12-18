from typing import Dict
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _processar_hierarquia_completa(self, texto_completo: str, no: Dict, idioma: str):
    try:
        texto_puro = no.get('texto_puro', '').strip()
        nivel = no.get('nivel', 0)
        titulo = no.get('titulo', 'Nó')

        if texto_puro and len(texto_puro) > 50:
            doc_no = self.nlp(texto_puro[:1_000_000])

            conceitos = self._extrair_conceitos_semanticos(doc_no, texto_puro, nivel)
            no['conceitos'] = conceitos

            ideias = self._extrair_ideias_principais(doc_no, texto_puro, nivel)
            no['ideias_principais'] = ideias

            resumo = self._gerar_resumo_contextual(doc_no, texto_puro, nivel, titulo, idioma)
            no['resumo_contextual'] = resumo

            logger.info(
                f"✓ '{titulo[:40]}' (nível {nivel}): "
                f"{len(conceitos)} conceitos + {len(ideias)} ideias + resumo ({len(resumo)} chars)"
            )

        else:
            no['conceitos'] = []
            no['ideias_principais'] = []
            no['resumo_contextual'] = ""

        for filho in no.get('filhos', []):
            self._processar_hierarquia_completa(texto_completo, filho, idioma)

    except Exception as e:
        logger.error(f"Erro ao processar nó: {e}", exc_info=True)
