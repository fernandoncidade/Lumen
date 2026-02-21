from typing import List, Dict
import re
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _detectar_secoes_avancado(self, texto: str, idioma: str = 'pt') -> List[Dict]:
    try:
        secoes = []
        linhas = self._preprocessar_linhas(texto)

        regex_parte_cond = r'^(?:PARTE|PART|arte|art)\s*([IVXLCDM\d]+)(?:[:.\-]?)(.*)$'
        regex_capitulo_cond = r'^(?:CAPITULO|CAPÍTULO|CHAPTER|CHAP|apítulo|apitulo|hapter)\s*(\d+|[IVXLCDM]+)(?:[:.\-]?)(.*)$'

        padroes_pt = [
            {'regex': r'^(?:PARTE|Parte|arte)\s+([IVXLCDM\d]+)\s*[:.\-]?\s*(.+)$', 'nivel': 1, 'tipo': 'parte_inline'},
            {'regex': r'^(?:PARTE|Parte|arte)\s+([IVXLCDM\d]+)\s*[:.\-]?\s*$', 'nivel': 1, 'tipo': 'parte_header'},
            {'regex': r'^(?:CAPÍTULO|Capítulo|CAP\.?|apítulo)\s+(\d+|[IVXLCDM]+)\s*[:.\-]?\s*(.*)$', 'nivel': 2, 'tipo': 'capitulo'},
            {'regex': r'^(\d+)\.\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.!?]{3,120})$', 'nivel': 2, 'tipo': 'capitulo_numerado'},
            {'regex': r'^(\d+\.\d+)[\s.\-]+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.!?]{3,120})$', 'nivel': 3, 'tipo': 'subcapitulo'},
            {'regex': r'^(\d+\.\d+\.\d+)[\s.\-]+(.+)$', 'nivel': 4, 'tipo': 'subsubcapitulo'},
        ]

        padroes_en = [
            {'regex': r'^(?:PART|Part|art)\s+([IVXLCDM\d]+)\s*[:.\-]?\s*(.+)$', 'nivel': 1, 'tipo': 'parte_inline'},
            {'regex': r'^(?:PART|Part|art)\s+([IVXLCDM\d]+)\s*[:.\-]?\s*$', 'nivel': 1, 'tipo': 'parte_header'},
            {'regex': r'^(?:CHAPTER|Chapter|CHAP\.?|hapter)\s+(\d+|[IVXLCDM]+)\s*[:.\-]?\s*(.*)$', 'nivel': 2, 'tipo': 'capitulo'},
            {'regex': r'^(\d+)\.\s+([A-Z][^.!?]{3,120})$', 'nivel': 2, 'tipo': 'capitulo_numerado'},
            {'regex': r'^(\d+\.\d+)[\s.\-]+([A-Z][^.!?]{3,120})$', 'nivel': 3, 'tipo': 'subcapitulo'},
            {'regex': r'^(\d+\.\d+\.\d+)[\s.\-]+(.+)$', 'nivel': 4, 'tipo': 'subsubcapitulo'},
        ]

        padroes = padroes_pt if idioma == 'pt' else padroes_en

        nivel_atual = 0
        ultima_parte = None

        i = 0
        while i < len(linhas):
            linha_limpa = linhas[i]
            linha_original = linha_limpa
            i += 1

            if not linha_limpa or len(linha_limpa) < 3:
                continue

            if self._linha_parece_sumario(linha_limpa):
                continue

            linha_limpa = self._corrigir_palavras_conhecidas(linha_limpa)
            variantes = self._variantes_para_match(linha_limpa)

            match_encontrado = False
            for padrao in padroes:
                tipo = padrao['tipo']
                nivel = padrao['nivel']

                m = re.match(padrao['regex'], linha_limpa, re.IGNORECASE)
                if not m:
                    m = re.match(padrao['regex'], variantes["original"], re.IGNORECASE)

                if not m:
                    m = re.match(padrao['regex'], variantes["sem_acentos"], re.IGNORECASE)

                if not m and tipo in ("parte_inline", "parte_header"):
                    m = re.match(regex_parte_cond, variantes["condensada"], re.IGNORECASE)
                    if m:
                        numero = (m.group(1) or "").strip()
                        resto = (m.group(2) or "").strip()
                        grupos = (numero, resto) if resto else (numero, )

                    else:
                        grupos = None

                elif not m and tipo == "capitulo":
                    m = re.match(regex_capitulo_cond, variantes["condensada"], re.IGNORECASE)
                    if m:
                        numero = (m.group(1) or "").strip()
                        resto = (m.group(2) or "").strip()
                        grupos = (numero, resto)

                    else:
                        grupos = None

                else:
                    grupos = m.groups() if m else None

                if not m and not grupos:
                    continue

                titulo = linha_limpa

                if tipo in ('parte_inline', 'parte_header'):
                    numero = grupos[0] if grupos else ''
                    subtitulo = ''

                    if len(grupos) > 1 and (grupos[1] or "").strip():
                        subtitulo = (grupos[1] or "").strip()

                    else:
                        subtitulo = self._proximo_titulo(linhas, i - 1)

                    titulo = (f"Parte {numero}" if idioma == 'pt' else f"Part {numero}")
                    if subtitulo:
                        titulo = f"{titulo}: {subtitulo}"

                elif tipo in ('capitulo', 'capitulo_numerado'):
                    numero = grupos[0] if grupos else ''
                    resto = (grupos[1] or '').strip() if (grupos and len(grupos) > 1) else ''
                    if idioma == 'pt':
                        titulo = f"Capítulo {numero}" + (f": {resto}" if resto else "")

                    else:
                        titulo = f"Chapter {numero}" + (f": {resto}" if resto else "")

                else:
                    if grupos and len(grupos) >= 2:
                        titulo = f"{grupos[0]} {grupos[1]}".strip()

                    elif grupos and len(grupos) == 1:
                        titulo = grupos[0].strip()

                if re.match(r'^[\d\.\s\-]+$', titulo):
                    continue

                secoes.append({
                    'titulo': titulo.strip(),
                    'nivel': nivel,
                    'posicao': i - 1,
                    'tipo': tipo
                })

                logger.debug(f"Detectado título: nivel={nivel}, tipo={tipo}, titulo='{titulo[:80]}'")
                nivel_atual = nivel
                if nivel == 1:
                    ultima_parte = len(secoes) - 1

                match_encontrado = True
                break

            if match_encontrado:
                continue

            if self._e_titulo_maiusculas(linha_limpa, linhas, i - 1):
                nivel = self._inferir_nivel_titulo(linha_limpa, nivel_atual, ultima_parte is not None)
                secoes.append({'titulo': linha_limpa, 'nivel': nivel, 'posicao': i - 1, 'tipo': 'titulo_maiusculas'})
                nivel_atual = nivel
                continue

            if self._e_titulo_isolado(linha_limpa, linhas, i - 1):
                nivel = min(nivel_atual + 1, 4) if nivel_atual > 0 else 3
                secoes.append({'titulo': linha_limpa, 'nivel': nivel, 'posicao': i - 1, 'tipo': 'titulo_isolado'})
                nivel_atual = nivel
                continue

        secoes.sort(key=lambda x: x['posicao'])
        return self._ajustar_niveis_relativos(secoes)

    except Exception as e:
        logger.error(f"Erro ao detectar seções avançado: {e}", exc_info=True)
        return []
