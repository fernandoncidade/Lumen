from source.utils.LogManager import LogManager

try:
    from PySide6.QtCore import QCoreApplication

except Exception:
    QCoreApplication = None

logger = LogManager.get_logger()

from source.modules.mapa.iaprocessador import (
    _carregar_modelo_nlp as pia__carregar_modelo_nlp,
    _detectar_idioma_texto as pia__detectar_idioma_texto,
    extrair_texto_pdf as pia_extrair_texto_pdf,
    extrair_texto_docx as pia_extrair_texto_docx,
    extrair_texto_txt as pia_extrair_texto_txt,
    extrair_texto as pia_extrair_texto,
    analisar_estrutura as pia_analisar_estrutura,
    _corrigir_caracteres_extraidos as pia__corrigir_caracteres_extraidos,
    _corrigir_palavras_conhecidas as pia__corrigir_palavras_conhecidas,
    _preprocessar_linhas as pia__preprocessar_linhas,
    _linha_parece_sumario as pia__linha_parece_sumario,
    _proximo_titulo as pia__proximo_titulo,
    _remover_acentos as pia__remover_acentos,
    _variantes_para_match as pia__variantes_para_match,
    _detectar_secoes_avancado as pia__detectar_secoes_avancado,
    _ajustar_niveis_relativos as pia__ajustar_niveis_relativos,
    _e_titulo_maiusculas as pia__e_titulo_maiusculas,
    _e_titulo_isolado as pia__e_titulo_isolado,
    _inferir_nivel_titulo as pia__inferir_nivel_titulo,
    _construir_arvore_hierarquica as pia__construir_arvore_hierarquica,
    _processar_hierarquia_completa as pia__processar_hierarquia_completa,
    _gerar_resumo_contextual as pia__gerar_resumo_contextual,
    _extrair_conceitos_semanticos as pia__extrair_conceitos_semanticos,
    _extrair_ideias_principais as pia__extrair_ideias_principais,
    _extrair_conceitos_tfidf as pia__extrair_conceitos_tfidf,
    _aplicar_tfidf_global as pia__aplicar_tfidf_global,
    _identificar_relacoes_semanticas as pia__identificar_relacoes_semanticas,
    _identificar_relacoes_avancadas as pia__identificar_relacoes_avancadas,
    _log_estrutura_completa as pia__log_estrutura_completa,
)


class ProcessadorIA:
    def __init__(self):
        self._tr = lambda s: s

        try:
            if QCoreApplication and QCoreApplication.instance():
                self._tr = lambda s: QCoreApplication.translate("App", s)

            self.nlp = None
            self.idioma_detectado = 'pt'
            self._carregar_modelo_nlp()

        except Exception as e:
            logger.error(f"Erro ao inicializar ProcessadorIA: {e}", exc_info=True)

    _carregar_modelo_nlp = pia__carregar_modelo_nlp
    _detectar_idioma_texto = pia__detectar_idioma_texto

    extrair_texto_pdf = pia_extrair_texto_pdf
    extrair_texto_docx = pia_extrair_texto_docx
    extrair_texto_txt = pia_extrair_texto_txt
    extrair_texto = pia_extrair_texto

    analisar_estrutura = pia_analisar_estrutura

    _corrigir_caracteres_extraidos = pia__corrigir_caracteres_extraidos
    _corrigir_palavras_conhecidas = pia__corrigir_palavras_conhecidas

    _preprocessar_linhas = pia__preprocessar_linhas
    _linha_parece_sumario = pia__linha_parece_sumario
    _proximo_titulo = pia__proximo_titulo
    _remover_acentos = pia__remover_acentos
    _variantes_para_match = pia__variantes_para_match

    _detectar_secoes_avancado = pia__detectar_secoes_avancado
    _ajustar_niveis_relativos = pia__ajustar_niveis_relativos
    _e_titulo_maiusculas = pia__e_titulo_maiusculas
    _e_titulo_isolado = pia__e_titulo_isolado
    _inferir_nivel_titulo = pia__inferir_nivel_titulo

    _construir_arvore_hierarquica = pia__construir_arvore_hierarquica
    _processar_hierarquia_completa = pia__processar_hierarquia_completa

    _gerar_resumo_contextual = pia__gerar_resumo_contextual
    _extrair_conceitos_semanticos = pia__extrair_conceitos_semanticos
    _extrair_ideias_principais = pia__extrair_ideias_principais
    _extrair_conceitos_tfidf = pia__extrair_conceitos_tfidf
    _aplicar_tfidf_global = pia__aplicar_tfidf_global

    _identificar_relacoes_semanticas = pia__identificar_relacoes_semanticas
    _identificar_relacoes_avancadas = pia__identificar_relacoes_avancadas

    _log_estrutura_completa = pia__log_estrutura_completa
