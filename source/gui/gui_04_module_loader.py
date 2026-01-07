from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import importlib
from typing import Iterable, List, Optional, Tuple
from source.gui.gui_02_interfaces import ModuleInterface


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def discover_plugin_imports(
    *,
    modules_dir: Optional[Path] = None,
    marker_filename: str = "*_module.py",
) -> List[str]:
    root = _repo_root()
    base_dir = modules_dir or (root / "source" / "modules")
    if not base_dir.exists():
        return []

    imports: List[str] = []
    for module_file in base_dir.glob(f"**/{marker_filename}"):
        try:
            rel = module_file.relative_to(root)

        except ValueError:
            continue

        import_path = ".".join(rel.with_suffix("").parts)
        imports.append(import_path)

    return sorted(set(imports))


def _instantiate_plugin(module_obj) -> ModuleInterface:
    if hasattr(module_obj, "create_plugin"):
        plugin = module_obj.create_plugin()

    elif hasattr(module_obj, "PLUGIN_CLASS"):
        plugin = module_obj.PLUGIN_CLASS()

    else:
        raise ValueError(
            "Plugin entrypoint inválido: defina `create_plugin()` ou `PLUGIN_CLASS` no module.py"
        )

    if not isinstance(plugin, ModuleInterface):
        raise TypeError(f"Plugin não implementa ModuleInterface: {type(plugin)!r}")

    return plugin


@dataclass(frozen=True)
class DiscoveredPlugin:
    import_path: str
    plugin: ModuleInterface


def discover_plugins(
    *,
    imports: Optional[Iterable[str]] = None,
) -> Tuple[List[DiscoveredPlugin], List[Tuple[str, Exception]]]:
    import_paths = list(imports) if imports is not None else discover_plugin_imports()
    plugins: List[DiscoveredPlugin] = []
    errors: List[Tuple[str, Exception]] = []

    for import_path in import_paths:
        try:
            module_obj = importlib.import_module(import_path)
            plugin = _instantiate_plugin(module_obj)
            plugins.append(DiscoveredPlugin(import_path=import_path, plugin=plugin))

        except Exception as e:
            errors.append((import_path, e))

    plugins.sort(key=lambda p: (getattr(p.plugin.meta, "order", 0), p.plugin.meta.name))
    return plugins, errors
