from PySide6.QtWidgets import QFileDialog, QApplication, QProgressDialog
from PySide6.QtCore import Qt, QCoreApplication
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_04_ProcessadorIA import ProcessadorIA

logger = LogManager.get_logger()

def importar_documento_ia(self):
    try:
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            QCoreApplication.translate("App", "Importar Documento"),
            self.caminho_persistente,
            QCoreApplication.translate("App", "Documentos (*.pdf *.docx *.txt)")
        )

        if not arquivo:
            return

        progress = QProgressDialog(
            QCoreApplication.translate("App", "Analisando documento com IA...\nIsso pode levar alguns minutos."),
            QCoreApplication.translate("App", "Cancelar"),
            0, 0, self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle(QCoreApplication.translate("App", "Lúmen"))
        progress.show()

        if self.processador_ia is None:
            progress.setLabelText(QCoreApplication.translate("App", "Carregando modelo de IA..."))
            QApplication.processEvents()
            self.processador_ia = ProcessadorIA()

        progress.setLabelText(QCoreApplication.translate("App", "Extraindo texto..."))
        QApplication.processEvents()
        texto = self.processador_ia.extrair_texto(arquivo)

        if not texto.strip():
            progress.close()
            logger.warning("Documento vazio ou não pôde ser lido")
            return

        progress.setLabelText(QCoreApplication.translate("App", "Analisando estrutura..."))
        QApplication.processEvents()
        hierarquia = self.processador_ia.analisar_estrutura(texto)

        progress.setLabelText(QCoreApplication.translate("App", "Gerando mapa mental..."))
        QApplication.processEvents()
        self.limpar_mapa()

        self._hierarquia_parent = {}
        self._hierarquia_children = {}
        self._modo_navegacao_hierarquia = False
        self._hierarquia_root = None

        raiz_no = self._gerar_mapa_de_hierarquia(hierarquia)
        if raiz_no:
            self._habilitar_navegacao_hierarquia(raiz_no)

        progress.close()
        logger.info(f"Mapa mental gerado com sucesso de: {arquivo}")

    except Exception as e:
        logger.error(f"Erro ao importar documento com IA: {str(e)}", exc_info=True)
        if 'progress' in locals():
            progress.close()
