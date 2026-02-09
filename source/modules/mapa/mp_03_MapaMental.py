from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsView, QGraphicsScene, QInputDialog, QColorDialog, QFileDialog, QToolBar, QFrame
from PySide6.QtCore import Qt, QRectF, QCoreApplication, QEvent
from PySide6.QtGui import QColor, QBrush, QPainter, QImage, QPalette
import json
import os
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
from source.modules.mapa.mp_01_NoConceito import NoConceito
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao


class MapaMental(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LogManager.get_logger()
        try:
            self.caminho_persistente = obter_caminho_persistente()
            self.modo_conexao = False
            self.no_origem = None
            self.nos = []
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

            layout.addWidget(self.toolbar)

            self.scene = QGraphicsScene()
            self.scene.setSceneRect(-2000, -2000, 4000, 4000)

            self.view = QGraphicsView(self.scene)
            self.view.setRenderHint(QPainter.Antialiasing)
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)

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
                self.scene.addItem(no)
                self.nos.append(no)

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
