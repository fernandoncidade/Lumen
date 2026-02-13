from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsView, QGraphicsScene, QInputDialog, 
                               QColorDialog, QFileDialog, QToolBar, QFrame, QApplication, QProgressDialog)
from PySide6.QtCore import Qt, QRectF, QCoreApplication, QEvent, QPointF, QTimer
from PySide6.QtGui import QColor, QBrush, QPainter, QImage, QPalette, QLinearGradient, QPen
from typing import Dict, List, Tuple
import json
import os
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
from source.modules.mapa.mp_01_NoConceito import NoConceito
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao
from source.modules.mapa.mp_04_ProcessadorIA import ProcessadorIA


class MapaScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._grid_step = 40
        self._grid_pen_light = QPen(QColor(255, 255, 255, 18), 1)
        self._grid_pen_dark = QPen(QColor(0, 0, 0, 22), 1)
        self._snap_enabled = True

    def drawBackground(self, painter: QPainter, rect: QRectF):
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor("#121212"))
        grad.setColorAt(0.5, QColor(25, 25, 25))
        grad.setColorAt(1.0, QColor("#1e1e1e"))
        painter.fillRect(rect, grad)

        left = int(rect.left()) - (int(rect.left()) % self._grid_step)
        top = int(rect.top()) - (int(rect.top()) % self._grid_step)

        painter.setPen(self._grid_pen_light)
        for x in range(left, int(rect.right()), self._grid_step):
            painter.drawLine(x, rect.top(), x, rect.bottom())

        for y in range(top, int(rect.bottom()), self._grid_step):
            painter.drawLine(rect.left(), y, rect.right(), y)

        painter.setPen(self._grid_pen_dark)
        strong = self._grid_step * 5
        left_s = int(rect.left()) - (int(rect.left()) % strong)
        top_s = int(rect.top()) - (int(rect.top()) % strong)
        for x in range(left_s, int(rect.right()), strong):
            painter.drawLine(x, rect.top(), x, rect.bottom())

        for y in range(top_s, int(rect.bottom()), strong):
            painter.drawLine(rect.left(), y, rect.right(), y)

    def snap(self, pos: QPointF) -> QPointF:
        if not self._snap_enabled:
            return pos

        step = self._grid_step
        return QPointF(round(pos.x() / step) * step, round(pos.y() / step) * step)


class SmoothGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self._current_zoom = 0

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            factor = zoom_in_factor
            self._current_zoom += 1

        else:
            factor = zoom_out_factor
            self._current_zoom -= 1

        if -15 <= self._current_zoom <= 25:
            self.scale(factor, factor)

    def animate_focus_on(self, item):
        self.centerOn(item)
        eff_timer = QTimer(self)
        c = QColor(255, 255, 255, 60)
        pen = QPen(c, 3)
        item.setPen(pen)
        def restore():
            item.setPen(QPen(Qt.black, 2))

        eff_timer.singleShot(420, restore)


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
            self.setup_ui()
            app = QCoreApplication.instance()
            if app:
                app.installEventFilter(self)

            self.atualizar_tema()

        except Exception as e:
            self.logger.error(f"Erro ao inicializar MapaMental: {str(e)}", exc_info=True)

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
            self.logger.error(f"Erro ao configurar interface do MapaMental: {str(e)}", exc_info=True)

    def atualizar_traducoes(self):
        try:
            self.btn_adicionar.setText(QCoreApplication.translate("App", "➕ Adicionar Conceito"))
            self.btn_conectar.setText(QCoreApplication.translate("App", "🔗 Conectar Conceitos"))
            self.btn_cor.setText(QCoreApplication.translate("App", "🎨 Cor"))
            self.btn_salvar.setText(QCoreApplication.translate("App", "💾 Salvar"))
            self.btn_carregar.setText(QCoreApplication.translate("App", "📂 Carregar"))
            self.btn_exportar.setText(QCoreApplication.translate("App", "📸 Exportar PNG"))
            self.btn_limpar.setText(QCoreApplication.translate("App", "🗑️ Limpar"))
            self.btn_importar_doc.setText(QCoreApplication.translate("App", "📄 Importar Documento (IA)"))
            self.btn_reorganizar.setText(QCoreApplication.translate("App", "🤖 Reorganizar com IA"))

            self.label_instrucoes.setText(
                QCoreApplication.translate("App",
                    "💡 Duplo-clique nos conceitos para editar | "
                    "Arraste para mover | "
                    "Use 'Conectar' para criar relações"
                )
            )

            if self.modo_conexao:
                self.btn_conectar.setText(QCoreApplication.translate("App", "🔗 Conectar (Ativo)"))

        except Exception as e:
            self.logger.error(f"Erro ao atualizar traduções do MapaMental: {str(e)}", exc_info=True)

    def adicionar_no(self):
        try:
            texto, ok = QInputDialog.getText(
                self, 
                QCoreApplication.translate("App", "Novo Conceito"), 
                QCoreApplication.translate("App", 
                                           "Digite o conceito:\n"
                                           "Ex: 'Tensão de Cisalhamento', 'Momento Fletor'"
                                           )
            )

            if ok and texto:
                if self.nos:
                    ultimo = self.nos[-1]
                    x = ultimo.scenePos().x() + 150
                    y = ultimo.scenePos().y()

                else:
                    x, y = 0, 0

                no = NoConceito(x, y, texto)
                if isinstance(self.scene, MapaScene):
                    pos = self.scene.snap(QPointF(x, y))
                    no.setPos(pos)

                self.scene.addItem(no)
                self.nos.append(no)
                self._expandir_area_se_necessario(no)

                if hasattr(self.view, "animate_focus_on"):
                    self.view.animate_focus_on(no)

        except Exception as e:
            self.logger.error(f"Erro ao adicionar nó: {str(e)}", exc_info=True)

    def toggle_modo_conexao(self):
        try:
            self.modo_conexao = self.btn_conectar.isChecked()

            if self.modo_conexao:
                self.btn_conectar.setText(QCoreApplication.translate("App", "🔗 Conectar (Ativo)"))
                self.btn_conectar.setStyleSheet("background-color: #28a745; color: white;")
                self.view.setDragMode(QGraphicsView.NoDrag)

                for no in self.nos:
                    no.mousePressEvent = lambda event, n=no: self.clicar_no_para_conectar(event, n)

            else:
                self.btn_conectar.setText(QCoreApplication.translate("App", "🔗 Conectar Conceitos"))
                self.btn_conectar.setStyleSheet("")
                self.view.setDragMode(QGraphicsView.ScrollHandDrag)
                self.no_origem = None

        except Exception as e:
            self.logger.error(f"Erro ao alternar modo de conexão: {str(e)}", exc_info=True)

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
            self.logger.error(f"Erro ao conectar nós: {str(e)}", exc_info=True)

    def mudar_cor(self):
        try:
            selecionados = [item for item in self.scene.selectedItems() if isinstance(item, NoConceito)]

            if not selecionados:
                return

            from PySide6.QtWidgets import QLabel, QPushButton, QGroupBox

            dialogo = QColorDialog(self)
            dialogo.setOption(QColorDialog.DontUseNativeDialog, True)
            dialogo.setOption(QColorDialog.ShowAlphaChannel, False)
            dialogo.setWindowTitle(QCoreApplication.translate("App", "advanced_color_picker"))
            dialogo.setModal(True)

            mapa_textos = {
                "Basic colors": "basic_colors",
                "&Basic colors": "basic_colors",
                "Custom colors": "custom_colors",
                "&Custom colors": "custom_colors",
                "Pick Screen Color": "pick_screen_color",
                "&Pick Screen Color": "pick_screen_color",
                "Add to Custom Colors": "add_to_custom_colors",
                "&Add to Custom Colors": "add_to_custom_colors",
                "Hue:": "hue",
                "&Hue:": "hue",
                "Sat:": "sat",
                "&Sat:": "sat",
                "Val:": "val",
                "&Val:": "val",
                "Red:": "red",
                "&Red:": "red",
                "Green:": "green",
                "&Green:": "green",
                "Blue:": "blue",
                "&Blue:": "blue",
                "HTML:": "html",
                "&HTML:": "html",
                "OK": "ok",
                "&OK": "ok",
                "Cancel": "cancel",
                "&Cancel": "cancel"
            }

            def normalizar(texto: str) -> str:
                return texto.strip().replace(":", "").replace("&", "")

            try:
                for label in dialogo.findChildren(QLabel):
                    txt = label.text().strip()
                    if not txt:
                        continue

                    txt_norm = normalizar(txt)
                    for chave_orig, chave_trad in mapa_textos.items():
                        if normalizar(chave_orig) == txt_norm:
                            traducao = QCoreApplication.translate("App", chave_trad)
                            label.setText(f"{traducao}:" if ":" in txt else traducao)
                            break

            except Exception:
                pass

            try:
                for btn in dialogo.findChildren(QPushButton):
                    txt = btn.text().strip()
                    if not txt:
                        continue

                    txt_norm = normalizar(txt)
                    for chave_orig, chave_trad in mapa_textos.items():
                        if normalizar(chave_orig) == txt_norm:
                            btn.setText(QCoreApplication.translate("App", chave_trad))
                            break

            except Exception:
                pass

            try:
                for gb in dialogo.findChildren(QGroupBox):
                    txt = gb.title().strip()
                    if not txt:
                        continue

                    txt_norm = normalizar(txt)
                    for chave_orig, chave_trad in mapa_textos.items():
                        if normalizar(chave_orig) == txt_norm:
                            gb.setTitle(QCoreApplication.translate("App", chave_trad))
                            break

            except Exception:
                pass

            if dialogo.exec():
                cor = dialogo.selectedColor()
                if cor.isValid():
                    for no in selecionados:
                        no.cor = cor
                        no.setBrush(QBrush(cor))

        except Exception as e:
            self.logger.error(f"Erro ao mudar cor: {str(e)}", exc_info=True)

    def salvar_mapa(self):
        try:
            arquivo, _ = QFileDialog.getSaveFileName(
                self, 
                QCoreApplication.translate("App", "Salvar Mapa Mental"), 
                os.path.join(self.caminho_persistente, "mapa_mental.json"), 
                QCoreApplication.translate("App", "JSON Files (*.json)")
            )

            if arquivo:
                dados = {
                    'nos': [
                        {
                            'texto': no.texto,
                            'x': no.scenePos().x(),
                            'y': no.scenePos().y(),
                            'cor': no.cor.name(),
                            'notas': no.notas
                        }
                        for no in self.nos
                    ],
                    'conexoes': [
                        {
                            'inicio': self.nos.index(linha.no_inicio),
                            'fim': self.nos.index(linha.no_fim)
                        }
                        for linha in self.scene.items() if isinstance(linha, LinhaConexao)
                    ]
                }

                with open(arquivo, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"Erro ao salvar mapa mental: {str(e)}", exc_info=True)

    def carregar_mapa(self):
        try:
            arquivo, _ = QFileDialog.getOpenFileName(
                self, 
                QCoreApplication.translate("App", "Carregar Mapa Mental"), 
                self.caminho_persistente, 
                QCoreApplication.translate("App", "JSON Files (*.json)")
            )

            if arquivo:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)

                self.limpar_mapa()

                for no_data in dados['nos']:
                    no = NoConceito(no_data['x'], no_data['y'], no_data['texto'], QColor(no_data['cor']))
                    no.notas = no_data.get('notas', '')
                    self.scene.addItem(no)
                    self.nos.append(no)

                for con_data in dados['conexoes']:
                    linha = LinhaConexao(self.nos[con_data['inicio']], self.nos[con_data['fim']])
                    self.scene.addItem(linha)

        except Exception as e:
            self.logger.error(f"Erro ao carregar mapa mental: {str(e)}", exc_info=True)

    def exportar_imagem(self):
        try:
            arquivo, _ = QFileDialog.getSaveFileName(
                self, 
                QCoreApplication.translate("App", "Exportar Mapa"), 
                os.path.join(self.caminho_persistente, "mapa_mental.png"), 
                QCoreApplication.translate("App", "PNG Files (*.png)")
            )

            if arquivo:
                rect = self.scene.itemsBoundingRect()
                image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
                image.fill(Qt.white)

                painter = QPainter(image)
                self.scene.render(painter, QRectF(image.rect()), rect)
                painter.end()

                image.save(arquivo)

        except Exception as e:
            self.logger.error(f"Erro ao exportar imagem: {str(e)}", exc_info=True)

    def limpar_mapa(self):
        try:
            self.scene.clear()
            self.nos.clear()
            self.no_origem = None

        except Exception as e:
            self.logger.error(f"Erro ao limpar mapa: {str(e)}", exc_info=True)

    def atualizar_tema(self):
        try:
            app = QCoreApplication.instance()
            pal = app.palette() if app else self.palette()

            bg_brush = pal.brush(QPalette.Base)

            self.scene.setBackgroundBrush(bg_brush)
            self.view.setBackgroundBrush(bg_brush)

            vp = self.view.viewport()
            vp.setPalette(pal)
            vp.setAutoFillBackground(True)

            for w in (self.view, vp):
                st = w.style()
                try:
                    st.unpolish(w)
                    st.polish(w)

                except Exception:
                    pass

                w.update()

            for sb in (self.view.horizontalScrollBar(), self.view.verticalScrollBar()):
                if not sb:
                    continue

                sb.setPalette(pal)

                if sb.styleSheet():
                    sb.setStyleSheet("")

                st = sb.style()

                try:
                    st.unpolish(sb)
                    st.polish(sb)

                except Exception:
                    pass

                sb.update()

        except Exception as e:
            self.logger.error(f"Erro ao aplicar tema dinâmico: {str(e)}", exc_info=True)

    def eventFilter(self, obj, event):
        try:
            tipos = (QEvent.ApplicationPaletteChange, QEvent.PaletteChange, QEvent.StyleChange,)

            try:
                tipos = tipos + (QEvent.ThemeChange,)

            except AttributeError:
                pass

            try:
                tipos = tipos + (QEvent.ColorSchemeChange,)

            except AttributeError:
                pass

            if event.type() in tipos:
                self.atualizar_tema()

        except Exception as e:
            self.logger.error(f"Erro no eventFilter de tema: {str(e)}", exc_info=True)

        return super().eventFilter(obj, event)

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
                self.logger.warning("Documento vazio ou não pôde ser lido")
                return

            progress.setLabelText(QCoreApplication.translate("App", "Analisando estrutura..."))
            QApplication.processEvents()
            hierarquia = self.processador_ia.analisar_estrutura(texto)

            progress.setLabelText(QCoreApplication.translate("App", "Gerando mapa mental..."))
            QApplication.processEvents()
            self.limpar_mapa()

            self._gerar_mapa_de_hierarquia(hierarquia)

            progress.close()
            self.logger.info(f"Mapa mental gerado com sucesso de: {arquivo}")

        except Exception as e:
            self.logger.error(f"Erro ao importar documento com IA: {str(e)}", exc_info=True)
            if 'progress' in locals():
                progress.close()

    def _gerar_mapa_de_hierarquia(self, hierarquia: Dict, x=0, y=0, nivel=0, pai=None):
        try:
            cores_nivel = [
                QColor("#8B4513"),  # Marrom - Tronco (Documento)
                QColor("#228B22"),  # Verde escuro - Galhos (Capítulos)
                QColor("#32CD32"),  # Verde médio - Ramos (Subcapítulos)
                QColor("#90EE90"),  # Verde claro - Sub-ramos
                QColor("#FFD700"),  # Amarelo - Folhas (Ideias)
            ]

            titulo = hierarquia.get('titulo', 'Conceito')
            nivel_hierarquico = hierarquia.get('nivel', nivel)
            tipo_no = hierarquia.get('tipo', 'secao')
            cor_no = cores_nivel[min(nivel, len(cores_nivel) - 1)]
            escala = max(1.2 - (nivel * 0.15), 0.5)
            no_principal = NoConceito(x, y, titulo, cor_no)
            no_principal.setScale(escala)
            self.scene.addItem(no_principal)
            self.nos.append(no_principal)

            if pai:
                linha = LinhaConexao(pai, no_principal)
                espessura = max(4 - nivel, 1)
                linha.setPen(QPen(QColor(101, 67, 33), espessura))
                self.scene.addItem(linha)

            info_associadas = []

            resumo = hierarquia.get('resumo_contextual', '')
            if resumo:
                simbolo_nivel = {
                    0: '📖',  # Documento
                    1: '📗',  # Parte
                    2: '📘',  # Capítulo
                    3: '📙',  # Subcapítulo
                    4: '📔'   # Sub-subcapítulo
                }.get(nivel, '📄')

                bloco_resumo = []
                bloco_resumo.append(f"{simbolo_nivel} RESUMO (Nível {nivel}):\n")
                bloco_resumo.append(f"{resumo}\n")
                bloco_resumo.append("━" * 60)
                info_associadas.append("".join(bloco_resumo))

            conceitos = hierarquia.get('conceitos', [])
            if conceitos:
                bloco_conceitos = []
                bloco_conceitos.append(f"\n🎯 CONCEITOS-CHAVE ({len(conceitos)}):\n")
                for idx, c in enumerate(conceitos[:10], 1):
                    tipo_icon = {
                        'entidade': '👤',
                        'termo_tecnico': '🔧',
                        'conceito': '💡'
                    }.get(c.get('tipo'), '•')

                    freq_info = f"[freq: {c['frequencia']}]" if c.get('frequencia') else ""
                    bloco_conceitos.append(
                        f"{idx}. {tipo_icon} {c['texto']} "
                        f"(importância: {c['importancia']:.2f}) {freq_info}\n"
                    )

                    if c.get('contextos') and len(c['contextos']) > 0:
                        contexto = c['contextos'][0][:150]
                        if len(c['contextos'][0]) > 150:
                            contexto += "..."

                        bloco_conceitos.append(f"   └─ Contexto: \"{contexto}\"\n")

                bloco_conceitos.append("━" * 60)
                info_associadas.append("".join(bloco_conceitos))

            ideias = hierarquia.get('ideias_principais', [])
            if ideias:
                bloco_ideias = []
                bloco_ideias.append(f"\n💡 IDEIAS PRINCIPAIS ({len(ideias)}):\n\n")
                for idx, ideia in enumerate(ideias[:8], 1):
                    importancia_barra = "█" * int(ideia['importancia'] * 10)
                    bloco_ideias.append(
                        f"{idx}. [{importancia_barra}] "
                        f"Importância: {ideia['importancia']:.2f}\n"
                    )

                    bloco_ideias.append(f"   \"{ideia['texto']}\"\n\n")

                bloco_ideias.append("━" * 60)
                info_associadas.append("".join(bloco_ideias))

            texto_puro = hierarquia.get('texto_puro', '')
            if texto_puro:
                num_palavras = len(texto_puro.split())
                num_caracteres = len(texto_puro)
                num_paragrafos = len([p for p in texto_puro.split('\n\n') if p.strip()])

                bloco_estatisticas = []
                bloco_estatisticas.append("\n📊 ESTATÍSTICAS:\n")
                bloco_estatisticas.append(f"   • Palavras: {num_palavras:,}\n")
                bloco_estatisticas.append(f"   • Caracteres: {num_caracteres:,}\n")
                bloco_estatisticas.append(f"   • Parágrafos: {num_paragrafos}\n")
                bloco_estatisticas.append(f"   • Nível hierárquico: {nivel}\n")
                bloco_estatisticas.append(f"   • Tipo: {tipo_no}\n")
                bloco_estatisticas.append("━" * 60)
                info_associadas.append("".join(bloco_estatisticas))

            filhos = hierarquia.get('filhos', [])
            if filhos:
                bloco_estrutura = []
                bloco_estrutura.append(f"\n🌿 SUB-SEÇÕES ({len(filhos)}):\n")
                for idx, filho in enumerate(filhos[:15], 1):
                    titulo_filho = filho.get('titulo', 'Sem título')[:50]
                    num_conceitos_filho = len(filho.get('conceitos', []))
                    num_ideias_filho = len(filho.get('ideias_principais', []))

                    bloco_estrutura.append(
                        f"   {idx}. {titulo_filho} "
                        f"({num_conceitos_filho} conceitos, {num_ideias_filho} ideias)\n"
                    )

                info_associadas.append("".join(bloco_estrutura))

            no_principal.info_associada = info_associadas
            no_principal._badge.setVisible(True)

            if ideias and nivel >= 2:
                import math
                num_ideias = len(ideias)
                raio_ideias = 120
                angulo_base = 0 if not pai else (x - (pai.scenePos().x() if pai else 0))

                cor_folha = QColor("#FFD700")

                for idx, ideia in enumerate(ideias[:6]):
                    angulo = angulo_base + (idx - num_ideias/2) * (180 / max(num_ideias, 1))
                    x_ideia = x + raio_ideias * math.cos(math.radians(angulo))
                    y_ideia = y + raio_ideias * math.sin(math.radians(angulo))

                    texto_resumido = ideia['texto'][:50] + "..." if len(ideia['texto']) > 50 else ideia['texto']

                    no_ideia = NoConceito(x_ideia, y_ideia, f"💡 {texto_resumido}", cor_folha)
                    no_ideia.setScale(0.7)

                    info_folha = []

                    bloco_header = []
                    bloco_header.append(f"💡 IDEIA PRINCIPAL #{idx+1}\n")
                    bloco_header.append("━" * 60)
                    info_folha.append("".join(bloco_header))

                    bloco_importancia = []
                    bloco_importancia.append(f"\n📊 Importância: {ideia['importancia']:.2f} ")
                    bloco_importancia.append("█" * int(ideia['importancia'] * 10) + "\n")
                    bloco_importancia.append("━" * 60)
                    info_folha.append("".join(bloco_importancia))

                    bloco_localizacao = []
                    bloco_localizacao.append(f"\n📍 LOCALIZAÇÃO:\n")
                    bloco_localizacao.append(f"   • Parágrafo: {ideia.get('paragrafo', 'N/A')}\n")
                    bloco_localizacao.append(f"   • Posição na sentença: {ideia.get('posicao_sentenca', 'N/A')}\n")
                    bloco_localizacao.append("━" * 60)
                    info_folha.append("".join(bloco_localizacao))

                    bloco_texto = []
                    bloco_texto.append(f"\n💬 TEXTO COMPLETO:\n\n")
                    bloco_texto.append(f"\"{ideia['texto']}\"\n")
                    bloco_texto.append("━" * 60)
                    info_folha.append("".join(bloco_texto))

                    bloco_vinculo = []
                    bloco_vinculo.append(f"\n🔗 Pertence a: {titulo[:40]}\n")
                    info_folha.append("".join(bloco_vinculo))

                    no_ideia.info_associada = info_folha
                    no_ideia._badge.setVisible(True)

                    self.scene.addItem(no_ideia)
                    self.nos.append(no_ideia)

                    linha_folha = LinhaConexao(no_principal, no_ideia)
                    linha_folha.setPen(QPen(QColor(34, 139, 34, 150), 1, Qt.DashLine))
                    self.scene.addItem(linha_folha)

                    self.logger.debug(f"✓ Folha visual criada: '{texto_resumido}' para '{titulo[:30]}'")

            if filhos:
                import math

                raio_base = 250
                raio = raio_base + (nivel * 60)

                if pai:
                    angulo_pai = math.atan2(y - pai.scenePos().y(), x - pai.scenePos().x())
                    offset_angular = math.degrees(angulo_pai)

                else:
                    offset_angular = -90

                abertura = 120 if nivel == 0 else 90
                angulo_inicio = offset_angular - (abertura / 2)
                angulo_step = abertura / max(len(filhos), 1)

                for i, filho in enumerate(filhos):
                    angulo = angulo_inicio + (i * angulo_step)
                    x_filho = x + raio * math.cos(math.radians(angulo))
                    y_filho = y + raio * math.sin(math.radians(angulo))

                    self._gerar_mapa_de_hierarquia(filho, x_filho, y_filho, nivel + 1, pai=no_principal )

            return no_principal

        except Exception as e:
            self.logger.error(f"Erro ao gerar mapa hierárquico: {e}", exc_info=True)
            return None

    def _criar_relacoes_ia(self, relacoes: List[Tuple]):
        try:
            mapa_nos = {no.texto.lower(): no for no in self.nos}

            for sujeito, verbo, objeto in relacoes[:20]:
                no_origem = mapa_nos.get(sujeito)
                no_destino = mapa_nos.get(objeto)

                if no_origem and no_destino and no_origem != no_destino:
                    ja_conectado = any(
                        (linha.no_inicio == no_origem and linha.no_fim == no_destino) or
                        (linha.no_inicio == no_destino and linha.no_fim == no_origem)
                        for linha in self.scene.items() if isinstance(linha, LinhaConexao)
                    )

                    if not ja_conectado:
                        linha = LinhaConexao(no_origem, no_destino)
                        self.scene.addItem(linha)

        except Exception as e:
            self.logger.error(f"Erro ao criar relações: {str(e)}", exc_info=True)

    def reorganizar_com_ia(self):
        try:
            if not self.nos:
                self.logger.warning("Nenhum conceito para reorganizar")
                return

            if self.processador_ia is None:
                self.processador_ia = ProcessadorIA()

            textos = [no.texto for no in self.nos]
            texto_completo = ". ".join(textos)

            doc = self.processador_ia.nlp(texto_completo)
            conceitos = self.processador_ia._extrair_conceitos_tfidf(doc, texto_completo)
            relacoes = self.processador_ia._identificar_relacoes_avancadas(doc, conceitos)
            conexoes_existentes = self._obter_conexoes_existentes()
            hierarquia = self._construir_hierarquia(conexoes_existentes)

            self._aplicar_layout_arvore(hierarquia)
            self._criar_relacoes_ia(relacoes)

            if self.nos and hasattr(self.view, "animate_focus_on"):
                self.view.animate_focus_on(self.nos[0])

            self.logger.info("Mapa reorganizado em formato de árvore com sucesso")

        except Exception as e:
            self.logger.error(f"Erro ao reorganizar com IA: {str(e)}", exc_info=True)

    def _obter_conexoes_existentes(self) -> Dict[int, List[int]]:
        conexoes = {i: [] for i in range(len(self.nos))}

        for item in self.scene.items():
            if isinstance(item, LinhaConexao):
                try:
                    idx_inicio = self.nos.index(item.no_inicio)
                    idx_fim = self.nos.index(item.no_fim)
                    conexoes[idx_inicio].append(idx_fim)
                    conexoes[idx_fim].append(idx_inicio)

                except ValueError:
                    continue

        return conexoes

    def _construir_hierarquia(self, conexoes: Dict[int, List[int]]) -> Dict:
        if not self.nos:
            return {}

        contagem_conexoes = [(i, len(conns)) for i, conns in conexoes.items()]
        contagem_conexoes.sort(key=lambda x: x[1], reverse=True)

        raiz_idx = contagem_conexoes[0][0] if contagem_conexoes else 0

        visitados = set()
        niveis = {raiz_idx: 0}
        filhos = {i: [] for i in range(len(self.nos))}
        pais = {i: None for i in range(len(self.nos))}

        fila = [raiz_idx]
        visitados.add(raiz_idx)

        while fila:
            atual = fila.pop(0)
            nivel_atual = niveis[atual]

            for vizinho in conexoes[atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    niveis[vizinho] = nivel_atual + 1
                    filhos[atual].append(vizinho)
                    pais[vizinho] = atual
                    fila.append(vizinho)

        for i in range(len(self.nos)):
            if i not in visitados:
                visitados.add(i)
                niveis[i] = 1
                filhos[raiz_idx].append(i)
                pais[i] = raiz_idx

        return {
            'raiz': raiz_idx,
            'niveis': niveis,
            'filhos': filhos,
            'pais': pais
        }

    def _aplicar_layout_arvore(self, hierarquia: Dict):
        if not hierarquia or 'raiz' not in hierarquia:
            return

        raiz_idx = hierarquia['raiz']
        filhos = hierarquia['filhos']
        niveis = hierarquia['niveis']

        ESPACAMENTO_VERTICAL = 150
        ESPACAMENTO_HORIZONTAL_BASE = 200

        nos_por_nivel = {}
        for idx, nivel in niveis.items():
            if nivel not in nos_por_nivel:
                nos_por_nivel[nivel] = []

            nos_por_nivel[nivel].append(idx)

        larguras = self._calcular_larguras_subarvore(raiz_idx, filhos, ESPACAMENTO_HORIZONTAL_BASE)
        self._posicionar_no_arvore(raiz_idx, filhos, larguras, x=0, y=0, espacamento_v=ESPACAMENTO_VERTICAL)

        if isinstance(self.scene, MapaScene):
            for no in self.nos:
                pos = self.scene.snap(no.scenePos())
                no.setPos(pos)

    def _calcular_larguras_subarvore(self, idx: int, filhos: Dict[int, List[int]], espacamento_base: float) -> Dict[int, float]:
        larguras = {}

        def calcular_recursivo(no_idx: int) -> float:
            filhos_no = filhos.get(no_idx, [])

            if not filhos_no:
                larguras[no_idx] = espacamento_base
                return espacamento_base

            largura_total = sum(calcular_recursivo(f) for f in filhos_no)
            larguras[no_idx] = max(largura_total, espacamento_base)
            return larguras[no_idx]

        calcular_recursivo(idx)
        return larguras

    def _posicionar_no_arvore(self, idx: int, filhos: Dict[int, List[int]], larguras: Dict[int, float], x: float, y: float, espacamento_v: float):
        self.nos[idx].setPos(x, y)
        self._expandir_area_se_necessario(self.nos[idx])

        filhos_no = filhos.get(idx, [])
        if not filhos_no:
            return

        largura_total_filhos = sum(larguras.get(f, 100) for f in filhos_no)
        x_inicio = x - (largura_total_filhos / 2)

        x_atual = x_inicio
        for filho_idx in filhos_no:
            largura_filho = larguras.get(filho_idx, 100)
            x_filho = x_atual + (largura_filho / 2)
            y_filho = y + espacamento_v

            self._posicionar_no_arvore(
                filho_idx, 
                filhos, 
                larguras, 
                x_filho, 
                y_filho, 
                espacamento_v
            )

            x_atual += largura_filho

    def _expandir_area_se_necessario(self, no):
        try:
            margem = 1000
            pos = no.scenePos()
            rect_atual = self.scene.sceneRect()

            precisa_expandir = False
            novo_left = rect_atual.left()
            novo_top = rect_atual.top()
            novo_right = rect_atual.right()
            novo_bottom = rect_atual.bottom()

            if pos.x() < rect_atual.left() + margem:
                novo_left = pos.x() - margem * 2
                precisa_expandir = True

            if pos.x() > rect_atual.right() - margem:
                novo_right = pos.x() + margem * 2
                precisa_expandir = True

            if pos.y() < rect_atual.top() + margem:
                novo_top = pos.y() - margem * 2
                precisa_expandir = True

            if pos.y() > rect_atual.bottom() - margem:
                novo_bottom = pos.y() + margem * 2
                precisa_expandir = True

            if precisa_expandir:
                nova_largura = novo_right - novo_left
                nova_altura = novo_bottom - novo_top
                self.scene.setSceneRect(novo_left, novo_top, nova_largura, nova_altura)
                self.logger.debug(
                    f"Área expandida para: x={novo_left:.0f}, y={novo_top:.0f}, "
                    f"w={nova_largura:.0f}, h={nova_altura:.0f}"
                )

        except Exception as e:
            self.logger.error(f"Erro ao expandir área: {str(e)}", exc_info=True)
