from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QSlider, QLabel, QComboBox, QTabWidget, QWidget, QSpinBox
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QIcon
from source.utils.FontManager import FontManager
from source.utils.LogManager import LogManager
from source.utils.IconUtils import get_icon_path
from .lta_22_pdf_toolbar import setup_pdf_toolbar
logger = LogManager.get_logger()

def setup_ui(self):
    try:
        layout = QVBoxLayout()

        controles = QHBoxLayout()

        self.btn_carregar = QPushButton()
        self.btn_carregar.clicked.connect(self.carregar_pdf)
        controles.addWidget(self.btn_carregar)

        self.btn_play = QPushButton()
        self.btn_play.clicked.connect(self.iniciar_leitura)
        controles.addWidget(self.btn_play)

        self.btn_pause = QPushButton()
        self.btn_pause.setEnabled(False)
        self.btn_pause.setCheckable(True)
        self.btn_pause.clicked.connect(self.pausar_leitura)
        controles.addWidget(self.btn_pause)

        self.btn_stop = QPushButton()
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.parar_leitura)
        controles.addWidget(self.btn_stop)

        controles.addStretch()
        layout.addLayout(controles)

        ajustes = QHBoxLayout()

        self.label_velocidade_titulo = QLabel()
        ajustes.addWidget(self.label_velocidade_titulo)

        self.slider_velocidade = QSlider(Qt.Horizontal)
        self.slider_velocidade.setRange(50, 250)
        self.slider_velocidade.setValue(150)
        self.slider_velocidade.setTickPosition(QSlider.TicksBelow)
        self.slider_velocidade.setTickInterval(25)
        ajustes.addWidget(self.slider_velocidade)

        self.label_velocidade = QLabel("150 wpm")
        self.slider_velocidade.valueChanged.connect(lambda v: self.label_velocidade.setText(f"{v} wpm"))
        self.slider_velocidade.valueChanged.connect(self._on_speed_changed)
        ajustes.addWidget(self.label_velocidade)

        self.label_volume = QLabel()
        ajustes.addWidget(self.label_volume)

        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(100)
        self.slider_volume.valueChanged.connect(self._on_volume_changed)
        ajustes.addWidget(self.slider_volume)

        self.label_fonte = QLabel()
        ajustes.addWidget(self.label_fonte)

        self.combo_fonte = QComboBox()
        self.combo_fonte.addItems(["6pt", "7pt", "8pt", "9pt", "10pt", "11pt", "12pt", "13pt", "14pt", "15pt", 
                                   "16pt", "17pt", "18pt", "19pt", "20pt", "21pt", "22pt", "23pt", "24pt"])

        try:
            config = FontManager.get_config()
            tamanho_salvo = config.get("size", 10)
            tamanho_texto = f"{tamanho_salvo}pt"

            if tamanho_texto in [self.combo_fonte.itemText(i) for i in range(self.combo_fonte.count())]:
                self.combo_fonte.setCurrentText(tamanho_texto)

            else:
                self.combo_fonte.setCurrentText("10pt")

        except Exception as e:
            logger.error(f"Erro ao carregar tamanho de fonte: {e}", exc_info=True)
            self.combo_fonte.setCurrentText("10pt")

        self.combo_fonte.currentTextChanged.connect(self.ajustar_fonte)
        ajustes.addWidget(self.combo_fonte)

        layout.addLayout(ajustes)

        self._content_stack = QTabWidget()

        text_tab = QWidget()
        text_layout = QVBoxLayout()

        text_toolbar = QHBoxLayout()

        self.btn_new = QPushButton(QCoreApplication.translate("App", "🆕 Novo"))
        self.btn_new.clicked.connect(lambda: getattr(self, "criar_texto")(confirmar=True))
        text_toolbar.addWidget(self.btn_new)

        self.btn_save = QPushButton(QCoreApplication.translate("App", "💾 Salvar Como"))
        self.btn_save.clicked.connect(lambda: getattr(self, "salvar_como")())
        text_toolbar.addWidget(self.btn_save)

        text_toolbar.addStretch()

        self.btn_bullets = QPushButton(QCoreApplication.translate("App", "• Marcadores"))
        self.btn_bullets.clicked.connect(lambda: getattr(self, "toggle_bullets")())
        text_toolbar.addWidget(self.btn_bullets)

        text_toolbar.addStretch()

        self.label_spacing = QLabel(QCoreApplication.translate("App", "Espaçamento:"))
        text_toolbar.addWidget(self.label_spacing)

        self.combo_spacing = QComboBox()
        self.combo_spacing.addItems(["1.0", "1.15", "1.5", "2.0"])
        self.combo_spacing.setCurrentText("1.0")
        self.combo_spacing.currentTextChanged.connect(lambda v: getattr(self, "set_line_spacing")(float(v)))
        text_toolbar.addWidget(self.combo_spacing)

        self.label_indent = QLabel(QCoreApplication.translate("App", "Recuo:"))
        text_toolbar.addWidget(self.label_indent)

        self.spin_indent = QSpinBox()
        self.spin_indent.setRange(0, 500)
        self.spin_indent.setValue(0)
        self.spin_indent.setSingleStep(5)
        self.spin_indent.valueChanged.connect(lambda v: getattr(self, "set_indent")(int(v)))
        text_toolbar.addWidget(self.spin_indent)

        self.label_margin = QLabel(QCoreApplication.translate("App", "Margem:"))
        text_toolbar.addWidget(self.label_margin)

        self.spin_margin = QSpinBox()
        self.spin_margin.setRange(0, 200)
        self.spin_margin.setValue(10)
        self.spin_margin.setSingleStep(1)
        self.spin_margin.valueChanged.connect(lambda v: getattr(self, "set_margins")(float(v)))
        text_toolbar.addWidget(self.spin_margin)

        text_layout.addLayout(text_toolbar)

        self.texto_area = QTextEdit()
        self.texto_area.setReadOnly(False)
        self.texto_area.setObjectName("leitor_texto_area")
        text_layout.addWidget(self.texto_area)
        text_tab.setLayout(text_layout)
        self._content_stack.addTab(text_tab, QCoreApplication.translate("App", "Texto"))

        pdf_tab = QWidget()
        pdf_layout = QVBoxLayout()

        try:
            from PySide6.QtPdfWidgets import QPdfView
            from PySide6.QtPdf import QPdfDocument

            self.pdf_doc = QPdfDocument(self)
            self.pdf_view = QPdfView(self)
            self.pdf_view.setDocument(self.pdf_doc)

            pdf_toolbar_layout = setup_pdf_toolbar(self)
            pdf_layout.addLayout(pdf_toolbar_layout)
            pdf_layout.addWidget(self.pdf_view)

        except Exception as e:
            logger.debug(f"QtPdf indisponível: {e}", exc_info=True)
            self.pdf_view = None
            self.pdf_doc = None
            try:
                pdf_toolbar_layout = setup_pdf_toolbar(self)
                pdf_layout.addLayout(pdf_toolbar_layout)

            except Exception as e:
                logger.debug(f"Erro ao configurar toolbar PDF: {e}", exc_info=True)

        pdf_tab.setLayout(pdf_layout)
        self._content_stack.addTab(pdf_tab, QCoreApplication.translate("App", "PDF"))

        layout.addWidget(self._content_stack)

        try:
            from PySide6.QtGui import QTextCursor, QTextCharFormat
            font = FontManager.get_font()
            doc = self.texto_area.document()
            doc.setDefaultFont(font)

        except Exception as e:
            logger.error(f"Erro ao obter fonte do FontManager: {e}", exc_info=True)

        regua_layout = QHBoxLayout()

        self.btn_regua = self.gerenciador_botoes.create_button()
        self.btn_regua.setIcon(QIcon(get_icon_path("ruler")))
        self.btn_regua.clicked.connect(self.toggle_regua_foco)
        self.btn_regua.setCheckable(True)
        regua_layout.addWidget(self.btn_regua)

        self.dica_regua = QLabel()
        self.dica_regua.setStyleSheet("color: #666; font-size: 10pt;")
        self.dica_regua.setWordWrap(True)
        regua_layout.addWidget(self.dica_regua)

        layout.addLayout(regua_layout)
        self.setLayout(layout)
        self.atualizar_traducoes()

    except Exception as e:
        logger.error(f"Erro ao configurar interface do Leitor Acessível: {str(e)}", exc_info=True)
