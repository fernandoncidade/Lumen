from __future__ import annotations
from typing import Optional
from PySide6.QtWidgets import QWidget
from source.gui.gui_02_interfaces import ModuleInterface, ModuleMeta, ModuleContext


class MatrizEisenhowerPlugin(ModuleInterface):
    _meta = ModuleMeta(
        id="matriz_eisenhower",
        name="🗂️ Matriz Eisenhower",
        version="1.0.0",
        description="Priorização por urgência/importância.",
        order=40,
        host_attr="eisenhower",
    )

    def __init__(self):
        self._widget: Optional[QWidget] = None
        self._context: Optional[ModuleContext] = None

    @property
    def meta(self) -> ModuleMeta:
        return self._meta

    def start(self, context: ModuleContext) -> None:
        self._context = context

    def get_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        if self._widget is None:
            from source.modules.mod_06_eisenhower import EisenhowerMatrixApp
            tradutor = None
            try:
                tradutor = getattr(self._context.host, "tradutor", None) if self._context else None

            except Exception:
                tradutor = None

            self._widget = EisenhowerMatrixApp(gerenciador_traducao=tradutor, embedded=True)
            if parent is not None:
                self._widget.setParent(parent)

        return self._widget

    def stop(self) -> None:
        w = self._widget
        if w is None:
            return

        try:
            if hasattr(w, "_stop_eisenhower_thread"):
                w._stop_eisenhower_thread()

        except Exception:
            pass

        try:
            w.deleteLater()

        except Exception:
            pass

        self._widget = None


PLUGIN_CLASS = MatrizEisenhowerPlugin


def create_plugin() -> MatrizEisenhowerPlugin:
    return MatrizEisenhowerPlugin()
