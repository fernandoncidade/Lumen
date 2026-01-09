from PySide6.QtWidgets import QTabWidget, QMessageBox, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _make_placeholder(text: str) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lay.addWidget(lbl)
    lay.addStretch(1)
    return w

def setup_ui(self) -> None:
    self.tabs = QTabWidget()
    self.setCentralWidget(self.tabs)

    self._lazy_tabs = {}

    def _tab_title(idx: int) -> str:
        titles = {
            0: QCoreApplication.translate("App", "📖 Leitor Acessível"),
            1: QCoreApplication.translate("App", "⏱️ Gestão de Tempo"),
            2: QCoreApplication.translate("App", "🧠 Mapas Mentais"),
            3: QCoreApplication.translate("App", "🎓 Método Feynman"),
            4: QCoreApplication.translate("App", "🗂️ Matriz Eisenhower"),
        }
        return titles.get(idx, "")

    def _register_lazy_tab(index: int, attr_name: str, factory):
        placeholder = _make_placeholder(QCoreApplication.translate("App", "Carregando módulo…"))
        self.tabs.addTab(placeholder, "")
        self._lazy_tabs[index] = {
            "attr": attr_name,
            "factory": factory,
            "loaded": False,
        }

    def _ensure_tab_loaded(index: int):
        try:
            info = self._lazy_tabs.get(index)
            if not info or info["loaded"]:
                return

            real_widget = info["factory"]()
            info["loaded"] = True
            setattr(self, info["attr"], real_widget)

            self.tabs.removeTab(index)
            self.tabs.insertTab(index, real_widget, "")
            self.tabs.setCurrentIndex(index)

            try:
                for i in range(self.tabs.count()):
                    self.tabs.setTabText(i, _tab_title(i))

            except Exception:
                pass

        except Exception as e:
            logger.critical(f"Erro crítico ao lazy-load da aba {index}: {e}", exc_info=True)
            titulo = QCoreApplication.translate("App", "Erro ao Carregar Módulo")
            msg_topo = QCoreApplication.translate("App", "Ocorreu um erro ao carregar o módulo:")
            msg_rodape = QCoreApplication.translate("App", "Verifique se todas as dependências estão instaladas.")
            QMessageBox.critical(self, titulo, f"{msg_topo}\n\n{str(e)}\n\n{msg_rodape}")
            raise

    def _factory_leitor():
        from source.modules.mod_01_leitor_acessivel import LeitorAcessivel
        w = LeitorAcessivel()

        try:
            w.btn_regua.toggled.connect(self.sincronizar_regua_menu)

        except Exception:
            pass

        return w

    def _factory_tempo():
        from source.modules.mod_03_gerenciador_tempo import GerenciadorTempo
        return GerenciadorTempo()

    def _factory_mapa():
        from source.modules.mod_04_mapa_mental import MapaMental
        return MapaMental()

    def _factory_feynman():
        from source.modules.mod_05_metodo_feynman import MetodoFeynman
        return MetodoFeynman()

    def _factory_eisenhower():
        from source.modules.mod_06_eisenhower import EisenhowerMatrixApp
        return EisenhowerMatrixApp(gerenciador_traducao=self.tradutor, embedded=True)

    _register_lazy_tab(0, "leitor", _factory_leitor)
    _register_lazy_tab(1, "gerenciador", _factory_tempo)
    _register_lazy_tab(2, "mapa", _factory_mapa)
    _register_lazy_tab(3, "feynman", _factory_feynman)
    _register_lazy_tab(4, "eisenhower", _factory_eisenhower)

    for i in range(self.tabs.count()):
        self.tabs.setTabText(i, _tab_title(i))

    self.tabs.currentChanged.connect(_ensure_tab_loaded)

    _ensure_tab_loaded(self.tabs.currentIndex())
