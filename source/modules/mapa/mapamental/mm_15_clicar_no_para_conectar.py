from PySide6.QtGui import QColor, QBrush
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao

logger = LogManager.get_logger()

def clicar_no_para_conectar(self, event, no):
    try:
        if not self.modo_conexao:
            return

        if self.no_origem is None:
            self.no_origem = no
            no.setBrush(QBrush(QColor("#ffc107")))

        else:
            if self.no_origem != no:
                linha = LinhaConexao(self.no_origem, no)
                self.scene.addItem(linha)

            self.no_origem.setBrush(QBrush(self.no_origem.cor))
            self.no_origem = None

    except Exception as e:
        logger.error(f"Erro ao conectar nós: {str(e)}", exc_info=True)
