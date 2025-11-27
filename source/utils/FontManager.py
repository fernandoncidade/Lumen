import json
from pathlib import Path
from PySide6.QtGui import QFont
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente

logger = LogManager.get_logger()


class FontManager:
    BASE_PERSIST = obter_caminho_persistente() or str(Path.home())
    CONFIG_FILE = Path(BASE_PERSIST) / "font_config.json"

    DEFAULT_CONFIG = {
        "family": "Arial",
        "size": 10,
        "bold": False,
        "italic": False,
        "underline": False,
    }

    @classmethod
    def _ensure_config_dir(cls):
        try:
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            logger.error(f"Erro ao criar diretório de configuração: {e}")

    @classmethod
    def get_config(cls) -> dict:
        try:
            cls._ensure_config_dir()
            if cls.CONFIG_FILE.exists():
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**cls.DEFAULT_CONFIG, **config}

            return cls.DEFAULT_CONFIG.copy()

        except Exception as e:
            logger.error(f"Erro ao ler configuração de fontes: {e}")
            return cls.DEFAULT_CONFIG.copy()

    @classmethod
    def save_config(cls, config: dict) -> bool:
        try:
            cls._ensure_config_dir()
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Configuração de fontes salva: {config}")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar configuração de fontes: {e}")
            return False

    @classmethod
    def get_font(cls) -> QFont:
        try:
            config = cls.get_config()
            font = QFont(config.get("family", cls.DEFAULT_CONFIG["family"]), config.get("size", cls.DEFAULT_CONFIG["size"]))
            font.setBold(bool(config.get("bold", False)))
            font.setItalic(bool(config.get("italic", False)))
            font.setUnderline(bool(config.get("underline", False)))
            return font

        except Exception as e:
            logger.error(f"Erro ao criar QFont: {e}")
            return QFont(cls.DEFAULT_CONFIG["family"], cls.DEFAULT_CONFIG["size"])

    @classmethod
    def get_html_style(cls) -> str:
        try:
            config = cls.get_config()
            font_family = config.get("family", cls.DEFAULT_CONFIG["family"])
            font_size = config.get("size", cls.DEFAULT_CONFIG["size"])
            font_weight = "bold" if config.get("bold", False) else "normal"
            font_style = "italic" if config.get("italic", False) else "normal"
            text_decoration = "underline" if config.get("underline", False) else "none"

            css = f"""
            <style>
                body {{
                    font-family: '{font_family}', monospace;
                    font-size: {font_size}pt;
                    font-weight: {font_weight};
                    font-style: {font_style};
                    text-decoration: {text_decoration};
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    margin: 0;
                    padding: 4px;
                }}
                pre {{
                    font-family: '{font_family}', monospace;
                    font-size: {font_size}pt;
                    font-weight: {font_weight};
                    font-style: {font_style};
                }}
            </style>
            """
            return css

        except Exception as e:
            logger.error(f"Erro ao gerar CSS de fontes: {e}")
            return "<style></style>"

    @classmethod
    def reset_to_default(cls) -> bool:
        return cls.save_config(cls.DEFAULT_CONFIG.copy())
