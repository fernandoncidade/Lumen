from __future__ import annotations
from typing import Optional
from PySide6.QtWidgets import QWidget
from source.gui.gui_02_interfaces import ModuleInterface, ModuleMeta, ModuleContext


class LeitorAcessivelPlugin(ModuleInterface):
    _meta = ModuleMeta(
        id="leitor_acessivel",
        name="📖 Leitor Acessível",
        version="1.0.0",
        description="Leitura acessível com TTS e ferramentas de PDF/texto.",
        order=0,
        host_attr="leitor",
    )

    def __init__(self):
        self._widget: Optional[QWidget] = None
        self._context: Optional[ModuleContext] = None

    @property
    def meta(self) -> ModuleMeta:
        return self._meta

    def get_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        if self._widget is None:
            from source.modules.leitor.lt_03_LeitorAcessivel import LeitorAcessivel
            self._widget = LeitorAcessivel()
            if parent is not None:
                self._widget.setParent(parent)

        return self._widget

    def start(self, context: ModuleContext) -> None:
        self._context = context
        context.event_bus.publish_type("module.started", {"id": self.meta.id}, source=self.meta.id)

    def stop(self) -> None:
        if self._widget is None:
            return

        try:
            if hasattr(self._widget, "cleanup"):
                self._widget.cleanup()

        finally:
            try:
                self._widget.deleteLater()

            except Exception:
                pass

            self._widget = None


PLUGIN_CLASS = LeitorAcessivelPlugin


def create_plugin() -> LeitorAcessivelPlugin:
    return LeitorAcessivelPlugin()
