from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QToolBar, QFrame
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_03_MapaMental import MapaScene
from source.modules.mapa.mp_03_MapaMental import SmoothGraphicsView

logger = LogManager.get_logger()

def setup_ui(self):
    try:
        layout = QVBoxLayout()
        self.toolbar = QToolBar()

        self.btn_adicionar = QPushButton()
        self.btn_adicionar.clicked.connect(self.adicionar_no)
        self.toolbar.addWidget(self.btn_adicionar)

        self.btn_conectar = QPushButton()
        self.btn_conectar.clicked.connect(self.toggle_modo_conexao)
        self.btn_conectar.setCheckable(True)
        self.toolbar.addWidget(self.btn_conectar)

        self.btn_cor = QPushButton()
        self.btn_cor.clicked.connect(self.mudar_cor)
        self.toolbar.addWidget(self.btn_cor)

        self.toolbar.addSeparator()

        self.btn_salvar = QPushButton()
        self.btn_salvar.clicked.connect(self.salvar_mapa)
        self.toolbar.addWidget(self.btn_salvar)

        self.btn_carregar = QPushButton()
        self.btn_carregar.clicked.connect(self.carregar_mapa)
        self.toolbar.addWidget(self.btn_carregar)

        self.btn_exportar = QPushButton()
        self.btn_exportar.clicked.connect(self.exportar_imagem)
        self.toolbar.addWidget(self.btn_exportar)

        self.btn_limpar = QPushButton()
        self.btn_limpar.clicked.connect(self.limpar_mapa)
        self.toolbar.addWidget(self.btn_limpar)

        self.toolbar.addSeparator()

        self.btn_importar_doc = QPushButton()
        self.btn_importar_doc.clicked.connect(self.importar_documento_ia)
        self.toolbar.addWidget(self.btn_importar_doc)

        self.btn_reorganizar = QPushButton()
        self.btn_reorganizar.clicked.connect(self.reorganizar_com_ia)
        self.toolbar.addWidget(self.btn_reorganizar)

        layout.addWidget(self.toolbar)

        self.scene = MapaScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)

        self.view = SmoothGraphicsView(self.scene)
        self.view.setFrameShape(QFrame.Box)
        self.view.setFrameShadow(QFrame.Plain)
        self.view.setLineWidth(1)
        self.view.setMidLineWidth(0)

        layout.addWidget(self.view)

        self.label_instrucoes = QLabel()
        layout.addWidget(self.label_instrucoes)

        self.setLayout(layout)
        self.atualizar_traducoes()
        self.atualizar_tema()

    except Exception as e:
        logger.error(f"Erro ao configurar interface do MapaMental: {str(e)}", exc_info=True)
