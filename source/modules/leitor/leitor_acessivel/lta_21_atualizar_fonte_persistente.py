from source.utils.LogManager import LogManager
from source.utils.FontManager import FontManager
from PySide6.QtGui import QTextCursor, QTextCharFormat

logger = LogManager.get_logger()

def atualizar_fonte_persistente(self):
    try:
        config = FontManager.get_config()
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

        tamanho = config.get("size", 10)
        tamanho_texto = f"{tamanho}pt"

        self.combo_fonte.blockSignals(True)
        if tamanho_texto in [self.combo_fonte.itemText(i) for i in range(self.combo_fonte.count())]:
            self.combo_fonte.setCurrentText(tamanho_texto)

        self.combo_fonte.blockSignals(False)

        logger.debug(f"Fonte do leitor sincronizada: {config}")

    except Exception as e:
        logger.error(f"Erro ao atualizar fonte persistente: {e}", exc_info=True)
