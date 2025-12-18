from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene
from PySide6.QtCore import QRectF, QCoreApplication, QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from typing import Dict
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente


class MapaScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._grid_step = 40
        self._grid_pen_light = QPen(QColor(255, 255, 255, 18), 1)
        self._grid_pen_dark = QPen(QColor(0, 0, 0, 22), 1)
        self._snap_enabled = True

    def drawBackground(self, painter: QPainter, rect: QRectF):
        from source.modules.mapa.mapamental.mm_01_drawBackground import drawBackground as _impl
        return _impl(self, painter, rect)

    def snap(self, pos: QPointF) -> QPointF:
        from source.modules.mapa.mapamental.mm_02_snap import snap as _impl
        return _impl(self, pos)


class SmoothGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self._current_zoom = 0

    def wheelEvent(self, event):
        from source.modules.mapa.mapamental.mm_03_wheelEvent import wheelEvent as _impl
        return _impl(self, event)

    def animate_focus_on(self, item):
        from source.modules.mapa.mapamental.mm_04_animate_focus_on import animate_focus_on as _impl
        return _impl(self, item)


class MapaMental(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LogManager.get_logger()
        try:
            self.caminho_persistente = obter_caminho_persistente()
            self.modo_conexao = False
            self.no_origem = None
            self.nos = []
            self.processador_ia = None

            self._modo_navegacao_hierarquia = False
            self._hierarquia_root = None
            self._hierarquia_parent = {}
            self._hierarquia_children = {}
            self._nos_expandidos = set()

            self.setup_ui()
            app = QCoreApplication.instance()
            if app:
                app.installEventFilter(self)

            self.atualizar_tema()

        except Exception as e:
            self.logger.error(f"Erro ao inicializar MapaMental: {str(e)}", exc_info=True)

    def setup_ui(self):
        from source.modules.mapa.mapamental.mm_11_setup_ui import setup_ui as _impl
        return _impl(self)

    def atualizar_traducoes(self):
        from source.modules.mapa.mapamental.mm_12_atualizar_traducoes import atualizar_traducoes as _impl
        return _impl(self)

    def adicionar_no(self):
        from source.modules.mapa.mapamental.mm_13_adicionar_no import adicionar_no as _impl
        return _impl(self)

    def toggle_modo_conexao(self):
        from source.modules.mapa.mapamental.mm_14_toggle_modo_conexao import toggle_modo_conexao as _impl
        return _impl(self)

    def clicar_no_para_conectar(self, event, no):
        from source.modules.mapa.mapamental.mm_15_clicar_no_para_conectar import clicar_no_para_conectar as _impl
        return _impl(self, event, no)

    def mudar_cor(self):
        from source.modules.mapa.mapamental.mm_16_mudar_cor import mudar_cor as _impl
        return _impl(self)

    def salvar_mapa(self):
        from source.modules.mapa.mapamental.mm_17_salvar_mapa import salvar_mapa as _impl
        return _impl(self)

    def carregar_mapa(self):
        from source.modules.mapa.mapamental.mm_18_carregar_mapa import carregar_mapa as _impl
        return _impl(self)

    def exportar_imagem(self):
        from source.modules.mapa.mapamental.mm_19_exportar_imagem import exportar_imagem as _impl
        return _impl(self)

    def limpar_mapa(self):
        from source.modules.mapa.mapamental.mm_20_limpar_mapa import limpar_mapa as _impl
        return _impl(self)

    def atualizar_tema(self):
        from source.modules.mapa.mapamental.mm_21_atualizar_tema import atualizar_tema as _impl
        return _impl(self)

    def importar_documento_ia(self):
        from source.modules.mapa.mapamental.mm_23_importar_documento_ia import importar_documento_ia as _impl
        return _impl(self)

    def _gerar_mapa_de_hierarquia(self, hierarquia: Dict, x=0, y=0, nivel=0, pai=None):
        from source.modules.mapa.mapamental.mm_24_gerar_mapa_de_hierarquia import _gerar_mapa_de_hierarquia as _impl
        return _impl(self, hierarquia, x=x, y=y, nivel=nivel, pai=pai)

    def _criar_relacoes_ia(self, relacoes):
        from source.modules.mapa.mapamental.mm_25_criar_relacoes_ia import _criar_relacoes_ia as _impl
        return _impl(self, relacoes)

    def reorganizar_com_ia(self):
        from source.modules.mapa.mapamental.mm_26_reorganizar_com_ia import reorganizar_com_ia as _impl
        return _impl(self)

    def _obter_conexoes_existentes(self):
        from source.modules.mapa.mapamental.mm_27_obter_conexoes_existentes import _obter_conexoes_existentes as _impl
        return _impl(self)

    def _construir_hierarquia(self, conexoes):
        from source.modules.mapa.mapamental.mm_28_construir_hierarquia import _construir_hierarquia as _impl
        return _impl(self, conexoes)

    def _aplicar_layout_arvore(self, hierarquia: Dict):
        from source.modules.mapa.mapamental.mm_29_aplicar_layout_arvore import _aplicar_layout_arvore as _impl
        return _impl(self, hierarquia)

    def _calcular_larguras_subarvore(self, idx: int, filhos, espacamento_base: float):
        from source.modules.mapa.mapamental.mm_30_calcular_larguras_subarvore import _calcular_larguras_subarvore as _impl
        return _impl(self, idx, filhos, espacamento_base)

    def _posicionar_no_arvore(self, idx: int, filhos, larguras, x: float, y: float, espacamento_v: float):
        from source.modules.mapa.mapamental.mm_31_posicionar_no_arvore import _posicionar_no_arvore as _impl
        return _impl(self, idx, filhos, larguras, x, y, espacamento_v)

    def _expandir_area_se_necessario(self, no):
        from source.modules.mapa.mapamental.mm_32_expandir_area_se_necessario import _expandir_area_se_necessario as _impl
        return _impl(self, no)

    def _atualizar_visibilidade_linhas(self):
        from source.modules.mapa.mapamental.mm_05_atualizar_visibilidade_linhas import _atualizar_visibilidade_linhas as _impl
        return _impl(self)

    def _instalar_handlers_nos(self):
        from source.modules.mapa.mapamental.mm_06_instalar_handlers_nos import _instalar_handlers_nos as _impl
        return _impl(self)

    def _aplicar_visibilidade_por_foco(self, foco, abrir_foco: bool):
        from source.modules.mapa.mapamental.mm_07_aplicar_visibilidade_por_foco import _aplicar_visibilidade_por_foco as _impl
        return _impl(self, foco, abrir_foco)

    def _clicar_no_para_expandir_hierarquia(self, no):
        from source.modules.mapa.mapamental.mm_08_clicar_no_para_expandir_hierarquia import _clicar_no_para_expandir_hierarquia as _impl
        return _impl(self, no)

    def _habilitar_navegacao_hierarquia(self, raiz_no):
        from source.modules.mapa.mapamental.mm_09_habilitar_navegacao_hierarquia import _habilitar_navegacao_hierarquia as _impl
        return _impl(self, raiz_no)

    def _configurar_hierarquia_por_indices(self, hierarquia: Dict):
        from source.modules.mapa.mapamental.mm_10_configurar_hierarquia_por_indices import _configurar_hierarquia_por_indices as _impl
        return _impl(self, hierarquia)

    def eventFilter(self, obj, event):
        from source.modules.mapa.mapamental.mm_22_eventFilter import eventFilter as _impl
        return _impl(self, obj, event)
