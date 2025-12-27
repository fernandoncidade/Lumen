from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QToolBar, QFrame, QMessageBox
from PySide6.QtCore import QCoreApplication, QPointF
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def setup_ui(self):
    try:
        from source.modules.mapa.mp_03_MapaMental import MapaScene, SmoothGraphicsView

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
                if getattr(self, "_lumen_layout_original_snapshot", None):
                    return

                nos = (getattr(self, "nos", []) or [])
                self._lumen_layout_original_snapshot = {
                    "positions": {no: no.pos() for no in nos},
                    "visible": {no: getattr(no, "isVisible", lambda: True)() for no in nos},
                    "modo_hierarquia": bool(getattr(self, "_modo_navegacao_hierarquia", False)),
                    "hierarquia_root": getattr(self, "_hierarquia_root", None),
                    "hierarquia_parent": dict(getattr(self, "_hierarquia_parent", {}) or {}),
                    "hierarquia_children": dict(getattr(self, "_hierarquia_children", {}) or {}),
                    "nos_expandidos": set(getattr(self, "_nos_expandidos", set()) or set()),
                    "freeze_on_click": bool(getattr(self, "_lumen_layout_freeze_on_click", False)),
                    "orientation": str(getattr(self, "_lumen_layout_orientation", "free") or "free"),
                }

            except Exception as e:
                logger.error(f"Erro ao salvar snapshot de layout original: {e}", exc_info=True)

        def _restaurar_layout_original():
            try:
                snap = getattr(self, "_lumen_layout_original_snapshot", None) or {}
                if not snap:
                    return False

                nos = (getattr(self, "nos", []) or [])

                vis_map = snap.get("visible", {}) or {}
                for no in nos:
                    try:
                        if no in vis_map:
                            no.setVisible(bool(vis_map[no]))

                        else:
                            no.setVisible(True)

                    except Exception:
                        pass

                pos_map = snap.get("positions", {}) or {}
                for no in nos:
                    if no in pos_map:
                        no.setPos(pos_map[no])

                sc = getattr(self, "scene", None)
                if sc is not None and hasattr(sc, "snap"):
                    for no in nos:
                        try:
                            no.setPos(sc.snap(no.pos()))

                        except Exception:
                            pass

                try:
                    self._modo_navegacao_hierarquia = bool(snap.get("modo_hierarquia", False))
                    self._hierarquia_root = snap.get("hierarquia_root", None)
                    self._hierarquia_parent = dict(snap.get("hierarquia_parent", {}) or {})
                    self._hierarquia_children = dict(snap.get("hierarquia_children", {}) or {})
                    self._nos_expandidos = set(snap.get("nos_expandidos", set()) or set())

                except Exception:
                    pass

                try:
                    self._lumen_layout_freeze_on_click = bool(snap.get("freeze_on_click", False))
                    self._lumen_layout_orientation = str(snap.get("orientation", "free") or "free")

                except Exception:
                    pass

                if hasattr(self, "_atualizar_visibilidade_linhas"):
                    self._atualizar_visibilidade_linhas()

                try:
                    if getattr(self, "scene", None) is not None and hasattr(self.scene, "itemsBoundingRect"):
                        br = self.scene.itemsBoundingRect()
                        if not br.isNull() and not br.isEmpty():
                            padding = 1400
                            alvo = br.adjusted(-padding, -padding, padding, padding)
                            atual = self.scene.sceneRect()
                            if atual.isNull() or atual.isEmpty():
                                self.scene.setSceneRect(alvo)

                            else:
                                self.scene.setSceneRect(atual.united(alvo))

                except Exception:
                    pass

                return True

            except Exception as e:
                logger.error(f"Erro ao restaurar layout original: {e}", exc_info=True)
                return False

        def _aplicar_layout_horizontal_por_rotacao():
            try:
                nos = getattr(self, "nos", []) or []
                if not nos:
                    return False

                hier = getattr(self, "_lumen_last_hierarquia", None)
                if isinstance(hier, dict) and "raiz" in hier and "filhos" in hier and "niveis" in hier:
                    self._aplicar_layout_arvore(hier, orientacao="horizontal")

                    if hasattr(self, "_atualizar_visibilidade_linhas"):
                        self._atualizar_visibilidade_linhas()

                    if hasattr(self.view, "animate_focus_on") and nos:
                        self.view.animate_focus_on(nos[hier.get("raiz", 0)] if hier else nos[0])

                    return True

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

                try:
                    from source.modules.mapa.mapamental.mm_34_layout_hierarquia_navegacao import _resolver_sobreposicoes_global
                    _resolver_sobreposicoes_global(self, nos=nos, apenas_visiveis=False, push_direcao="right")
                    _resolver_sobreposicoes_global(self, nos=nos, apenas_visiveis=False, push_direcao="down")

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

                    self._lumen_layout_orientation = "vertical"
                    self._lumen_reorg_layout_state = 1
                    return

                if estado == 1:
                    if _aplicar_layout_horizontal_por_rotacao():
                        self._lumen_layout_orientation = "horizontal"
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
