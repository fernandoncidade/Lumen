from PySide6.QtWidgets import QTabWidget, QMessageBox
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def setup_ui(self) -> None:
    self.tabs = QTabWidget()
    self.setCentralWidget(self.tabs)

    try:
        from source.modules import (LeitorAcessivel, GerenciadorTempo, MapaMental, MetodoFeynman, EisenhowerMatrixApp)

        self.leitor = LeitorAcessivel()
        self.tabs.addTab(self.leitor, "")

        self.leitor.btn_regua.toggled.connect(self.sincronizar_regua_menu)

        self.gerenciador = GerenciadorTempo()
        self.tabs.addTab(self.gerenciador, "")

        self.mapa = MapaMental()
        self.tabs.addTab(self.mapa, "")

        self.feynman = MetodoFeynman()
        self.tabs.addTab(self.feynman, "")

        self.eisenhower = EisenhowerMatrixApp(gerenciador_traducao=self.tradutor, embedded=True)
        self.tabs.addTab(self.eisenhower, "")

    except Exception as e:
        logger.critical(f"Erro crítico ao carregar módulos: {e}", exc_info=True)
        titulo = QCoreApplication.translate("App", "Erro ao Carregar Módulos")
        msg_topo = QCoreApplication.translate("App", "Ocorreu um erro ao carregar os módulos:")
        msg_rodape = QCoreApplication.translate("App", "Verifique se todas as dependências estão instaladas.")
        QMessageBox.critical(self, titulo, f"{msg_topo}\n\n{str(e)}\n\n{msg_rodape}")
        raise
