from __future__ import annotations
from typing import Optional
from PySide6.QtWidgets import QWidget
from source.gui.gui_02_interfaces import ModuleInterface, ModuleMeta, ModuleContext


class GestaoTempoPlugin(ModuleInterface):
    _meta = ModuleMeta(
        id="gestao_tempo",
        name="⏱️ Gestão de Tempo",
        version="1.0.0",
        description="Pomodoro, tarefas e gerenciamento de tempo.",
        order=10,
        host_attr="gerenciador",
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
            from source.modules.tempo import GerenciadorTempo
            self._widget = GerenciadorTempo()
            if parent is not None:
                self._widget.setParent(parent)

        return self._widget

    def stop(self) -> None:
        w = self._widget
        if w is None:
            return

        try:
            if hasattr(w, "cleanup"):
                w.cleanup()

        except Exception:
            pass

        try:
            w.deleteLater()

        except Exception:
            pass

        self._widget = None


PLUGIN_CLASS = GestaoTempoPlugin


def create_plugin() -> GestaoTempoPlugin:
    return GestaoTempoPlugin()
