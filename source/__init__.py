import importlib
from typing import Any

__all__ = ["EstudoAcessivel"]

def __getattr__(name: str) -> Any:
    if name == "EstudoAcessivel":
        mod = importlib.import_module("source.gui_01_estudo_acessivel")
        return getattr(mod, "EstudoAcessivel")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
