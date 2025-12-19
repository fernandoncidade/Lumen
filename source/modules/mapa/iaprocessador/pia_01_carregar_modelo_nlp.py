import sys
import importlib
from pathlib import Path

import spacy
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _carregar_modelo_nlp(self):
    def _criar_nlp_fallback_basico(idioma: str):
        class _DocSimples:
            def __init__(self, text: str):
                self.text = text or ""

            @property
            def sents(self):
                return [self]

            @property
            def ents(self):
                return []

            @property
            def noun_chunks(self):
                return []

        class _NLPSimples:
            def __init__(self, lang: str):
                self.lang = lang
                self.max_length = 2_000_000

            @property
            def pipe_names(self):
                return []

            def add_pipe(self, name: str):
                return None

            def __call__(self, text: str):
                return _DocSimples(text)

        return _NLPSimples(idioma or "pt")

    def _base_dir_exec() -> Path:
        try:
            return Path(sys.executable).resolve().parent

        except Exception:
            return Path.cwd()

    def _carregar_por_modulo(nome_modelo: str):
        try:
            mod = importlib.import_module(nome_modelo)
            fn = getattr(mod, "load", None)
            if callable(fn):
                nlp = fn()
                logger.info(f"Modelo spaCy carregado via {nome_modelo}.load()")
                return nlp

        except Exception as e:
            logger.debug(f"Falha ao carregar via {nome_modelo}.load(): {e}")

        return None

    def _resolver_pasta_versionada_no_dist(nome_modelo: str) -> Path | None:
        raiz = _base_dir_exec() / nome_modelo
        if not raiz.exists():
            return None

        if (raiz / "config.cfg").exists():
            return raiz

        candidatos = sorted([p for p in raiz.glob(f"{nome_modelo}-*") if p.is_dir()])
        for p in reversed(candidatos):
            if (p / "config.cfg").exists():
                return p

        try:
            cfg = next(raiz.rglob("config.cfg"), None)
            if cfg:
                return cfg.parent

        except Exception:
            pass

        return None

    def _tentar_carregar_modelo_por_pasta(nome_modelo: str):
        pasta = _resolver_pasta_versionada_no_dist(nome_modelo)
        if not pasta:
            return None

        try:
            nlp = spacy.load(str(pasta))
            logger.info(f"Modelo spaCy carregado por PATH (dist): {nome_modelo} -> {pasta}")
            return nlp

        except Exception as e:
            logger.debug(f"Falha ao carregar spaCy por PATH para '{nome_modelo}' em '{pasta}': {e}")
            return None

    try:
        self._nlp_modo_reduzido = False

        candidatos = [
            ("pt_core_news_lg", "pt"),
            ("en_core_web_lg", "en"),
            ("pt_core_news_sm", "pt"),
            ("en_core_web_sm", "en"),
        ]

        ultimo_erro = None
        self.nlp = None

        for nome_modelo, idioma in candidatos:
            nlp1 = _carregar_por_modulo(nome_modelo)
            if nlp1 is not None:
                self.nlp = nlp1
                self.idioma_detectado = idioma
                break

            try:
                self.nlp = spacy.load(nome_modelo)
                self.idioma_detectado = idioma
                logger.info(f"Modelo spaCy carregado: {nome_modelo} | pipes={getattr(self.nlp, 'pipe_names', [])}")
                break

            except OSError as e:
                ultimo_erro = e

                nlp2 = _tentar_carregar_modelo_por_pasta(nome_modelo)
                if nlp2 is not None:
                    self.nlp = nlp2
                    self.idioma_detectado = idioma
                    break

        if self.nlp is None:
            logger.warning(
                "Nenhum modelo spaCy encontrado/carregado. "
                "Tentando spacy.blank(...) + sentencizer (recursos reduzidos)."
            )
            self._nlp_modo_reduzido = True
            self.idioma_detectado = getattr(self, "idioma_detectado", "pt") or "pt"

            try:
                self.nlp = spacy.blank("pt" if self.idioma_detectado == "pt" else "en")
                if "sentencizer" not in self.nlp.pipe_names:
                    self.nlp.add_pipe("sentencizer")

            except ModuleNotFoundError as e:
                logger.error(
                    f"spaCy não conseguiu inicializar (módulo ausente: {e}). "
                    "Ativando fallback básico.",
                    exc_info=True,
                )
                self.nlp = _criar_nlp_fallback_basico(self.idioma_detectado)

            if ultimo_erro:
                logger.error(f"Detalhe do último erro ao carregar modelo: {ultimo_erro}")

        if not callable(self.nlp):
            logger.error("NLP inválido após inicialização; ativando fallback básico.")
            self._nlp_modo_reduzido = True
            self.idioma_detectado = getattr(self, "idioma_detectado", "pt") or "pt"
            self.nlp = _criar_nlp_fallback_basico(self.idioma_detectado)

        self.nlp.max_length = 2_000_000
        logger.info(
            f"NLP configurado: idioma={self.idioma_detectado}, "
            f"max_length={self.nlp.max_length}, modo_reduzido={self._nlp_modo_reduzido}"
        )

    except Exception as e:
        logger.error(f"Erro ao carregar modelo spaCy: {e}", exc_info=True)
        self._nlp_modo_reduzido = True
        self.idioma_detectado = getattr(self, "idioma_detectado", "pt") or "pt"
        self.nlp = _criar_nlp_fallback_basico(self.idioma_detectado)
        self.nlp.max_length = 2_000_000
