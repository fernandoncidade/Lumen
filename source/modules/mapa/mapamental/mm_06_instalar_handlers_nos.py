from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _instalar_handlers_nos(self):
    try:
        for no in self.nos:
            if not hasattr(no, "_lumen_mousePressEvent_original"):
                no._lumen_mousePressEvent_original = no.mousePressEvent

            def _handler(event, n=no):
                try:
                    if event.button() == Qt.LeftButton:
                        if self.modo_conexao:
                            self.clicar_no_para_conectar(event, n)
                            return

                        if self._modo_navegacao_hierarquia:
                            self._clicar_no_para_expandir_hierarquia(n)

                    return n._lumen_mousePressEvent_original(event)

                except Exception as ex:
                    logger.error(f"Erro no handler de clique do nó: {ex}", exc_info=True)
                    return n._lumen_mousePressEvent_original(event)

            no.mousePressEvent = _handler

    except Exception as e:
        logger.error(f"Erro ao instalar handlers nos nós: {e}", exc_info=True)
