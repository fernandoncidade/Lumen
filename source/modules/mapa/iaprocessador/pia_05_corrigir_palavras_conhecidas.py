import re
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _corrigir_palavras_conhecidas(self, linha: str) -> str:
    try:
        correcoes = {
            # Português
            r'\barte\s+(I{1,3}|IV|V|VI{0,3}|IX|X|[0-9]+)\b': r'Parte \1',
            r'\bARTE\s+(I{1,3}|IV|V|VI{0,3}|IX|X|[0-9]+)\b': r'PARTE \1',
            r'\bapítulo\s+(I{1,3}|IV|V|VI{0,3}|IX|X|[0-9]+|\d+)\b': r'Capítulo \1',
            r'\bAPÍTULO\s+(I{1,3}|IV|V|VI{0,3}|IX|X|[0-9]+|\d+)\b': r'CAPÍTULO \1',
            r'\bSTILO\b': 'ESTILO',
            r'\bstilo\b': 'estilo',
            r'\bSeção\b': 'Seção',
            r'\bEÇÃO\b': 'SEÇÃO',
            
            # Inglês
            r'\bart\s+(I{1,3}|IV|V|VI{0,3}|IX|X|[0-9]+)\b': r'Part \1',
            r'\bART\s+(I{1,3}|IV|V|VI{0,3}|IX|X|[0-9]+)\b': r'PART \1',
            r'\bhapter\s+(I{1,3}|IV|V|VI{0,3}|IX|X|[0-9]+|\d+)\b': r'Chapter \1',
            r'\bHAPTER\s+(I{1,3}|IV|V|VI{0,3}|IX|X|[0-9]+|\d+)\b': r'CHAPTER \1',
        }

        linha_corrigida = linha
        for padrao, substituicao in correcoes.items():
            linha_corrigida = re.sub(padrao, substituicao, linha_corrigida, flags=re.IGNORECASE)

        if re.match(r'^(arte|apítulo|art|hapter)\s+', linha_corrigida, re.IGNORECASE):
            linha_corrigida = linha_corrigida[0].upper() + linha_corrigida[1:]

        return linha_corrigida

    except Exception as e:
        logger.error(f"Erro ao corrigir palavras conhecidas: {e}", exc_info=True)
        return linha
