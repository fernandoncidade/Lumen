from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QComboBox, QListWidget, QSplitter, QFrame
from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import QIcon, QPalette
from source.utils.LogManager import LogManager
from source.utils.IconUtils import get_icon_path
logger = LogManager.get_logger()

def setup_ui(self):
    try:
        layout = QVBoxLayout()

        self.label_instrucoes = QLabel()
        self.label_instrucoes.setWordWrap(True)
        self.label_instrucoes.setMaximumHeight(60)
        self.label_instrucoes.setAlignment(Qt.AlignTop)
        layout.addWidget(self.label_instrucoes)

        frame_principal = QFrame(self)
        frame_principal.setFrameShape(QFrame.Box)
        frame_principal.setFrameShadow(QFrame.Plain)
        frame_principal.setLineWidth(1)
        frame_principal.setMidLineWidth(0)

        layout_frame = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        painel_esquerdo = QWidget(self)
        layout_esquerdo = QVBoxLayout()

        self.label_meus_conceitos = QLabel()
        layout_esquerdo.addWidget(self.label_meus_conceitos)

        self.lista_conceitos = QListWidget()
        self.lista_conceitos.itemClicked.connect(self.selecionar_conceito)
        self.lista_conceitos.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lista_conceitos.customContextMenuRequested.connect(self.mostrar_menu_contexto)
        layout_esquerdo.addWidget(self.lista_conceitos)

        botoes_conceitos = QHBoxLayout()

        self.btn_novo = QPushButton()
        self.btn_novo.clicked.connect(self.novo_conceito)
        botoes_conceitos.addWidget(self.btn_novo)

        self.btn_deletar = QPushButton()
        self.btn_deletar.clicked.connect(self.deletar_conceito)
        botoes_conceitos.addWidget(self.btn_deletar)

        layout_esquerdo.addLayout(botoes_conceitos)
        painel_esquerdo.setLayout(layout_esquerdo)

        painel_direito = QWidget(self)
        layout_direito = QVBoxLayout()

        self.label_conceito = QLabel()
        self.label_conceito.setWordWrap(True)
        layout_direito.addWidget(self.label_conceito)

        self.input_titulo = QTextEdit()
        self.input_titulo.setObjectName("feynman_user_input")
        layout_direito.addWidget(self.input_titulo)

        self.label_passo1 = QLabel()
        self.label_passo1.setWordWrap(True)
        layout_direito.addWidget(self.label_passo1)

        self.texto_explicacao = QTextEdit()
        self.texto_explicacao.setObjectName("feynman_user_input")
        layout_direito.addWidget(self.texto_explicacao)

        self.label_passo2 = QLabel()
        self.label_passo2.setWordWrap(True)
        layout_direito.addWidget(self.label_passo2)

        self.texto_lacunas = QTextEdit()
        self.texto_lacunas.setObjectName("feynman_user_input")
        layout_direito.addWidget(self.texto_lacunas)

        self.label_passo3 = QLabel()
        self.label_passo3.setWordWrap(True)
        layout_direito.addWidget(self.label_passo3)

        self.texto_revisao = QTextEdit()
        self.texto_revisao.setObjectName("feynman_user_input")
        layout_direito.addWidget(self.texto_revisao)

        layout_status = QHBoxLayout()
        self.label_nivel = QLabel()
        layout_status.addWidget(self.label_nivel)

        self.combo_dominio = QComboBox()
        layout_status.addWidget(self.combo_dominio)
        layout_direito.addLayout(layout_status)

        self.btn_salvar = self.gerenciador_botoes.create_button()
        self.btn_salvar.setIcon(QIcon(get_icon_path("save")))
        self.btn_salvar.clicked.connect(self.salvar_conceito_atual)
        self.btn_salvar.setMaximumWidth(16777215)
        layout_direito.addWidget(self.btn_salvar)

        painel_direito.setLayout(layout_direito)

        splitter.addWidget(painel_esquerdo)
        splitter.addWidget(painel_direito)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout_frame.addWidget(splitter)
        frame_principal.setLayout(layout_frame)

        layout.addWidget(frame_principal)
        self.setLayout(layout)

        from PySide6.QtWidgets import QApplication

        def _apply_window_as_base(widget):
            if widget is None:
                return

            app = QApplication.instance()
            if app is None:
                return

            app_pal = app.palette()
            window_color = app_pal.color(QPalette.Window)

            pal = widget.palette()
            pal.setColor(QPalette.Base, window_color)
            pal.setColor(QPalette.AlternateBase, window_color)

            try:
                is_combo = isinstance(widget, QComboBox)

            except Exception:
                is_combo = False

            if is_combo:
                pal.setColor(QPalette.Button, window_color)

            widget.setPalette(pal)

            vp = getattr(widget, "viewport", None)
            if callable(vp):
                try:
                    widget.viewport().setAutoFillBackground(True)
                    widget.viewport().setPalette(pal)

                except Exception:
                    pass

            else:
                widget.setAutoFillBackground(True)

            view = getattr(widget, "view", None)
            if callable(view):
                try:
                    v = view()
                    if v is not None:
                        v.setPalette(pal)
                        try:
                            v.viewport().setAutoFillBackground(True)
                            v.viewport().setPalette(pal)

                        except Exception:
                            pass

                except Exception:
                    pass

        def _sync_feynman_backgrounds():
            try:
                _apply_window_as_base(self.input_titulo)
                _apply_window_as_base(self.texto_explicacao)
                _apply_window_as_base(self.texto_lacunas)
                _apply_window_as_base(self.texto_revisao)
                _apply_window_as_base(self.combo_dominio)
                _apply_window_as_base(self.lista_conceitos)

            except Exception as e:
                logger.debug(f"Falha ao sincronizar fundos do Método Feynman via QPalette: {e}", exc_info=True)

        class _PaletteThemeSyncFilter(QObject):
            def eventFilter(self, obj, event):
                et = event.type()
                tipos = (QEvent.ApplicationPaletteChange, QEvent.PaletteChange, QEvent.StyleChange, QEvent.ThemeChange,)

                try:
                    tipos = tipos + (QEvent.ColorSchemeChange,)

                except AttributeError:
                    pass

                if et in tipos:
                    _sync_feynman_backgrounds()

                return super().eventFilter(obj, event)

        _sync_feynman_backgrounds()

        self._feynman_palette_sync_filter = _PaletteThemeSyncFilter(self)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self._feynman_palette_sync_filter)

        self.atualizar_traducoes()
        self.atualizar_lista()
        self.conceito_atual = None

    except Exception as e:
        logger.error(f"Erro ao configurar interface do MetodoFeynman: {str(e)}", exc_info=True)
