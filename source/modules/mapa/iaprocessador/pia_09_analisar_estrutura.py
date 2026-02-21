from typing import Dict
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def analisar_estrutura(self, texto: str) -> Dict:
    try:
        logger.info("=== INICIANDO ANÁLISE HIERÁRQUICA PROFUNDA ===")

        idioma = self._detectar_idioma_texto(texto)
        logger.info(f"Idioma detectado: {idioma}")

        secoes_raw = self._detectar_secoes_avancado(texto, idioma)
        logger.info(f"✓ {len(secoes_raw)} seções estruturais detectadas")

        arvore_secoes = self._construir_arvore_hierarquica(texto, secoes_raw)
        logger.info("✓ Árvore hierárquica base construída")

        self._processar_hierarquia_completa(texto, arvore_secoes, idioma)
        logger.info("✓ Conceitos e ideias principais extraídos")

        self._aplicar_tfidf_global(texto, arvore_secoes)
        logger.info("✓ Análise TF-IDF aplicada")

        relacoes_globais = self._identificar_relacoes_semanticas(arvore_secoes)
        arvore_secoes['relacoes'] = relacoes_globais
        logger.info(f"✓ {len(relacoes_globais)} relações semânticas identificadas")

        self._log_estrutura_completa(arvore_secoes)

        return arvore_secoes

    except Exception as e:
        logger.error(f"Erro ao analisar estrutura: {e}", exc_info=True)
        return {"titulo": "Documento", "conceitos": [], "ideias_principais": [], "relacoes": [], "filhos": []}
