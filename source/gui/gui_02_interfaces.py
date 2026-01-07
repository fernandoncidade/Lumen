from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from PySide6.QtWidgets import QWidget
from source.gui.gui_03_events import EventBus


@dataclass(frozen=True)
class ModuleMeta:
    id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    order: int = 0
    host_attr: str = ""


@dataclass
class ModuleContext:
    event_bus: EventBus
    app: Any
    host: Any


class ModuleInterface(ABC):
    @property
    @abstractmethod
    def meta(self) -> ModuleMeta:
        raise NotImplementedError

    @abstractmethod
    def get_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        """Retorna o widget principal do módulo (PySide6)."""

    def start(self, context: ModuleContext) -> None:
        """Inicia o módulo dentro do host (ou standalone)."""

    def stop(self) -> None:
        """Finaliza o módulo e libera recursos (threads, arquivos temporários, etc.)."""
