from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QToolBar, QFrame, QMessageBox
from PySide6.QtCore import QCoreApplication, QPointF
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

        AVISO_IA_ALPHA_KEY = "aviso_ia_alpha"

        AVISO_IA_ALPHA_FALLBACK_PT = (
            "Ao utilizar este recurso, considere que ele se encontra em fase inicial de desenvolvimento (versão alfa). "
            "Como todo sistema ainda em evolução, apresenta limitações conhecidas e comportamentos passíveis de ajustes. "
            "Recomenda-se, portanto, seu uso com cautela, expectativa calibrada e a devida paciência, enquanto o processo "
            "de refinamento, correção de falhas e otimização contínua está em andamento."
        )

        def _mostrar_aviso_ia_alpha_uma_vez(flag_attr: str):
            try:
                if getattr(self, flag_attr, False):
                    return

                setattr(self, flag_attr, True)

                aviso = QCoreApplication.translate("App", AVISO_IA_ALPHA_KEY)
                if aviso == AVISO_IA_ALPHA_KEY:
                    aviso = AVISO_IA_ALPHA_FALLBACK_PT

                QMessageBox.warning(
                    self,
                    QCoreApplication.translate("App", "Lúmen"),
                    aviso,
                    QMessageBox.Ok
                )

            except Exception as e:
                logger.error(f"Erro ao exibir aviso IA alfa: {e}", exc_info=True)

        def _snapshot_layout_original_se_necessario():
            try:
                if getattr(self, "_lumen_layout_original_positions", None):
                    return

                self._lumen_layout_original_positions = {no: no.pos() for no in (getattr(self, "nos", []) or [])}

            except Exception as e:
                logger.error(f"Erro ao salvar snapshot de layout original: {e}", exc_info=True)

        def _restaurar_layout_original():
            try:
                orig = getattr(self, "_lumen_layout_original_positions", None) or {}
                if not orig:
                    return False

                for no in (getattr(self, "nos", []) or []):
                    if no in orig:
                        no.setPos(orig[no])

                if isinstance(getattr(self, "scene", None), MapaScene):
                    for no in (getattr(self, "nos", []) or []):
                        try:
                            no.setPos(self.scene.snap(no.pos()))

                        except Exception:
                            pass

                if hasattr(self, "_atualizar_visibilidade_linhas"):
                    self._atualizar_visibilidade_linhas()

                return True

            except Exception as e:
                logger.error(f"Erro ao restaurar layout original: {e}", exc_info=True)
                return False

        def _aplicar_layout_horizontal_por_rotacao():
            try:
                nos = getattr(self, "nos", []) or []
                if not nos:
                    return False

                pts_antes = [no.pos() for no in nos]
                cx_antes = sum(p.x() for p in pts_antes) / len(pts_antes)
                cy_antes = sum(p.y() for p in pts_antes) / len(pts_antes)

                novos = {}
                for no in nos:
                    p = no.pos()
                    novos[no] = QPointF(p.y(), p.x())

                pts_depois = list(novos.values())
                cx_depois = sum(p.x() for p in pts_depois) / len(pts_depois)
                cy_depois = sum(p.y() for p in pts_depois) / len(pts_depois)

                dx = cx_antes - cx_depois
                dy = cy_antes - cy_depois

                for no in nos:
                    no.setPos(novos[no] + QPointF(dx, dy))

                if isinstance(getattr(self, "scene", None), MapaScene):
                    for no in nos:
                        try:
                            no.setPos(self.scene.snap(no.pos()))

                        except Exception:
                            pass

                if hasattr(self, "_atualizar_visibilidade_linhas"):
                    self._atualizar_visibilidade_linhas()

                if hasattr(self.view, "animate_focus_on") and nos:
                    self.view.animate_focus_on(nos[0])

                return True

            except Exception as e:
                logger.error(f"Erro ao aplicar layout horizontal: {e}", exc_info=True)
                return False

        def _on_importar_documento_ia():
            _mostrar_aviso_ia_alpha_uma_vez("_lumen_aviso_ia_alpha_exibido_importar")
            self.importar_documento_ia()

        def _on_reorganizar_com_ia_toggle():
            _mostrar_aviso_ia_alpha_uma_vez("_lumen_aviso_ia_alpha_exibido_reorganizar")

            try:
                if not (getattr(self, "nos", []) or []):
                    return

                estado = int(getattr(self, "_lumen_reorg_layout_state", 0) or 0)

                if estado == 0:
                    _snapshot_layout_original_se_necessario()
                    self.reorganizar_com_ia()
                    self._lumen_reorg_layout_state = 1
                    return

                if estado == 1:
                    if _aplicar_layout_horizontal_por_rotacao():
                        self._lumen_reorg_layout_state = 2

                    return

                if _restaurar_layout_original():
                    self._lumen_reorg_layout_state = 0

                else:
                    self._lumen_reorg_layout_state = 0

            except Exception as e:
                logger.error(f"Erro no toggle de reorganização: {e}", exc_info=True)

        self.btn_importar_doc = QPushButton()
        self.btn_importar_doc.clicked.connect(_on_importar_documento_ia)
        self.toolbar.addWidget(self.btn_importar_doc)

        self.btn_reorganizar = QPushButton()
        self.btn_reorganizar.clicked.connect(_on_reorganizar_com_ia_toggle)
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
