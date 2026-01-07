from __future__ import annotations
from typing import Optional
from PySide6.QtWidgets import QWidget
from source.gui.gui_02_interfaces import ModuleInterface, ModuleMeta, ModuleContext


class MapasMentaisPlugin(ModuleInterface):
    _meta = ModuleMeta(
        id="mapas_mentais",
        name="🧠 Mapas Mentais",
        version="1.0.0",
        description="Criação e navegação de mapas mentais.",
        order=20,
        host_attr="mapa",
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
            from source.modules.mapa import MapaMental
            self._widget = MapaMental()
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


PLUGIN_CLASS = MapasMentaisPlugin


def create_plugin() -> MapasMentaisPlugin:
    return MapasMentaisPlugin()
