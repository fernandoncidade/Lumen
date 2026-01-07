from PySide6.QtWidgets import QTabWidget, QMessageBox, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

try:
    from source.gui.ui.ui_25_detachable_tabs import DetachableTabWidget

except Exception:
    DetachableTabWidget = None

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
    self.tabs = DetachableTabWidget() if DetachableTabWidget is not None else QTabWidget()
    self.setCentralWidget(self.tabs)

    self._lazy_tabs = {}
    self._tab_module_ids = []

    try:
        from source.gui.gui_04_module_loader import discover_plugins
        self._plugins, self._plugin_errors = discover_plugins()

    except Exception as e:
        logger.error(f"Falha ao descobrir plugins: {e}", exc_info=True)
        self._plugins, self._plugin_errors = [], []

    self._plugins_by_id = {p.plugin.meta.id: p.plugin for p in self._plugins}

    tab_order = [
        "leitor_acessivel",
        "gestao_tempo",
        "mapas_mentais",
        "metodo_feynman",
        "matriz_eisenhower",
    ]

    if getattr(self, "only_module_ids", None):
        allowed = set(self.only_module_ids)
        tab_order = [mid for mid in tab_order if mid in allowed]
        logger.debug(f"[SETUP_UI] Filtered tab_order for only_module_ids={self.only_module_ids}: {tab_order}")

    def _tab_title_from_id(module_id: str) -> str:
        titles = {
            "leitor_acessivel": QCoreApplication.translate("App", "📖 Leitor Acessível"),
            "gestao_tempo": QCoreApplication.translate("App", "⏱️ Gestão de Tempo"),
            "mapas_mentais": QCoreApplication.translate("App", "🧠 Mapas Mentais"),
            "metodo_feynman": QCoreApplication.translate("App", "🎓 Método Feynman"),
            "matriz_eisenhower": QCoreApplication.translate("App", "🗂️ Matriz Eisenhower"),
        }
        return titles.get(module_id, module_id)

    def _register_lazy_tab(module_id: str, attr_name: str):
        placeholder = _make_placeholder(QCoreApplication.translate("App", "Carregando módulo…"))
        self.tabs.addTab(placeholder, "")
        index = self.tabs.count() - 1
        self._tab_module_ids.append(module_id)
        self._lazy_tabs[index] = {
            "attr": attr_name,
            "module_id": module_id,
            "loaded": False,
        }

    def _ensure_tab_loaded(index: int):
        try:
            if getattr(self, "_suppress_lazy_load", False):
                return

            info = self._lazy_tabs.get(index)
            if not info or info.get("loaded"):
                return

            module_id = info.get("module_id")
            plugin = self._plugins_by_id.get(module_id)
            if plugin is None:
                raise RuntimeError(f"Plugin não encontrado para module_id={module_id}")

            try:
                if getattr(self, "_module_context", None) is not None:
                    plugin.start(self._module_context)

            except Exception:
                pass

            real_widget = plugin.get_widget()
            info["loaded"] = True
            setattr(self, info["attr"], real_widget)

            if module_id == "leitor_acessivel":
                try:
                    if hasattr(real_widget, "btn_regua"):
                        real_widget.btn_regua.toggled.connect(self.sincronizar_regua_menu)

                except Exception:
                    pass

            try:
                from PySide6.QtCore import QSignalBlocker
                blocker = QSignalBlocker(self.tabs)

            except Exception:
                blocker = None

            try:
                prev_current = self.tabs.currentIndex()
                try:
                    self._suppress_lazy_load = True

                except Exception:
                    pass

                self.tabs.removeTab(index)
                self.tabs.insertTab(index, real_widget, _tab_title_from_id(module_id))

                try:
                    if prev_current >= 0 and prev_current < self.tabs.count():
                        self.tabs.setCurrentIndex(prev_current)

                except Exception:
                    pass

            finally:
                try:
                    if blocker is not None:
                        del blocker

                except Exception:
                    pass

                try:
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: setattr(self, "_suppress_lazy_load", False))

                except Exception:
                    try:
                        self._suppress_lazy_load = False

                    except Exception:
                        pass

        except Exception as e:
            logger.critical(f"Erro crítico ao lazy-load da aba {index}: {e}", exc_info=True)
            titulo = QCoreApplication.translate("App", "Erro ao Carregar Módulo")
            msg_topo = QCoreApplication.translate("App", "Ocorreu um erro ao carregar o módulo:")
            msg_rodape = QCoreApplication.translate("App", "Verifique se todas as dependências estão instaladas.")
            QMessageBox.critical(self, titulo, f"{msg_topo}\n\n{str(e)}\n\n{msg_rodape}")
            raise

    attr_by_id = {
        "leitor_acessivel": "leitor",
        "gestao_tempo": "gerenciador",
        "mapas_mentais": "mapa",
        "metodo_feynman": "feynman",
        "matriz_eisenhower": "eisenhower",
    }

    provided_tabs = getattr(self, "provided_tabs", {}) or {}
    _provided_indices = set()
    logger.debug(f"[SETUP_UI] provided_tabs keys: {list(provided_tabs.keys())}")

    for module_id in tab_order:
        attr_name = attr_by_id.get(module_id, module_id)

        if module_id in provided_tabs:
            widget, title = provided_tabs[module_id]
            logger.debug(f"[SETUP_UI] Adding provided tab: module_id={module_id} title={title!r}")
            self.tabs.addTab(widget, title or _tab_title_from_id(module_id))
            idx = self.tabs.count() - 1
            _provided_indices.add(idx)
            self._tab_module_ids.append(module_id)
            logger.debug(f"[SETUP_UI] After addTab: index={idx} actual_title={self.tabs.tabText(idx)!r}")
            setattr(self, attr_name, widget)
            continue

        if module_id not in self._plugins_by_id:
            logger.warning(f"Plugin ausente para aba: {module_id}")
            continue

        _register_lazy_tab(module_id, attr_name)

    for i in range(self.tabs.count()):
        if i in _provided_indices:
            continue

        mid = self._tab_module_ids[i] if i < len(self._tab_module_ids) else ""
        self.tabs.setTabText(i, _tab_title_from_id(mid))

    self._ensure_tab_loaded = _ensure_tab_loaded
    self.tabs.currentChanged.connect(_ensure_tab_loaded)

    try:
        if hasattr(self.tabs, "detach_requested"):
            self.tabs.detach_requested.connect(self.detach_module_tab)

    except Exception:
        pass

    _ensure_tab_loaded(self.tabs.currentIndex())
