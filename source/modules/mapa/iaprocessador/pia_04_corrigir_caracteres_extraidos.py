import re
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _corrigir_caracteres_extraidos(self, texto: str) -> str:
    try:
        linhas = texto.split('\n')
        linhas_corrigidas = []

        for i, linha in enumerate(linhas):
            linha_corrigida = linha

            if i > 0 and linhas[i-1].strip():
                linha_anterior = linhas[i-1].strip()

                if len(linha_anterior) <= 15 and linha_anterior.isupper():
                    if linha.strip() and (linha.strip()[0].isupper() or linha.strip().isupper()):
                        possivel_titulo = f"{linha_anterior} {linha.strip()}"

                        if re.match(r'(?:PARTE|PART|CAPÍTULO|CHAPTER)', possivel_titulo, re.IGNORECASE):
                            if linhas_corrigidas and linhas_corrigidas[-1] == linhas[i-1]:
                                linhas_corrigidas.pop()
                                linha_corrigida = possivel_titulo

            linha_corrigida = self._corrigir_palavras_conhecidas(linha_corrigida)
            linhas_corrigidas.append(linha_corrigida)

        return '\n'.join(linhas_corrigidas)

    except Exception as e:
        logger.error(f"Erro ao corrigir caracteres extraídos: {e}", exc_info=True)
        return texto
