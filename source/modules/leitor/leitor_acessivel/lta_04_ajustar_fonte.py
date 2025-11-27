from source.utils.LogManager import LogManager
from source.utils.FontManager import FontManager
from PySide6.QtGui import QTextCursor, QTextCharFormat

logger = LogManager.get_logger()

def ajustar_fonte(self, tamanho):
    try:
        config = FontManager.get_config()

        novo_tamanho = int(tamanho.replace("pt", ""))
        config["size"] = novo_tamanho

        FontManager.save_config(config)

        font = FontManager.get_font()
        try:
            doc = self.texto_area.document()
            doc.setDefaultFont(font)

            if not doc.isEmpty():
                cursor = QTextCursor(doc)
                cursor.select(QTextCursor.Document)
                fmt = QTextCharFormat()
                fmt.setFont(font)
                cursor.mergeCharFormat(fmt)

        except Exception as e:
            logger.error(f"Erro ao aplicar fonte no documento: {e}", exc_info=True)

        logger.debug(f"Tamanho de fonte ajustado para: {novo_tamanho}pt")

    except Exception as e:
        logger.error(f"Erro ao ajustar fonte: {str(e)}", exc_info=True)
