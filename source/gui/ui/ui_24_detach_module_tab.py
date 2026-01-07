from __future__ import annotations
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


def detach_module_tab(self, index: int) -> None:
    try:
        if not hasattr(self, "_tab_module_ids") or index < 0 or index >= len(self._tab_module_ids):
            return

        module_id = None
        try:
            if hasattr(self, "_lazy_tabs") and isinstance(self._lazy_tabs, dict):
                module_id = (self._lazy_tabs.get(index) or {}).get("module_id")

        except Exception:
            module_id = None

        if not module_id:
            module_id = self._tab_module_ids[index]

        try:
            if hasattr(self, "_ensure_tab_loaded"):
                self._ensure_tab_loaded(index)

        except Exception:
            pass

        widget = self.tabs.widget(index)
        title = self.tabs.tabText(index)

        try:
            self._suppress_lazy_load = True

        except Exception:
            pass

        try:
            from PySide6.QtCore import QSignalBlocker
            blocker = QSignalBlocker(self.tabs)

        except Exception:
            blocker = None

        try:
            self.tabs.removeTab(index)

            try:
                if index < len(self._tab_module_ids) and self._tab_module_ids[index] == module_id:
                    self._tab_module_ids.pop(index)

                elif module_id in self._tab_module_ids:
                    self._tab_module_ids.pop(self._tab_module_ids.index(module_id))

            except Exception:
                pass

            try:
                if hasattr(self, "_lazy_tabs") and isinstance(self._lazy_tabs, dict):
                    new_lazy = {}
                    for k, v in self._lazy_tabs.items():
                        if k < index:
                            new_lazy[k] = v

                        elif k > index:
                            new_lazy[k - 1] = v

                    self._lazy_tabs = new_lazy

            except Exception:
                pass

            try:
                if hasattr(self, "_lazy_tabs") and isinstance(self._lazy_tabs, dict):
                    rebuilt = []
                    for i in range(self.tabs.count()):
                        info = self._lazy_tabs.get(i)
                        if info and info.get("module_id"):
                            rebuilt.append(info["module_id"])

                        else:
                            rebuilt.append(self._tab_module_ids[i] if i < len(self._tab_module_ids) else "")

                    self._tab_module_ids = rebuilt

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

        if widget is None:
            return

        try:
            widget.setParent(None)

        except Exception as e:
            logger.error(f"Falha ao desvincular widget: {e}")

        from source.gui_01_estudo_acessivel import EstudoAcessivel

        detached = EstudoAcessivel(
            only_module_ids=[module_id],
            detached=True,
            detached_origin=self,
            provided_tabs={module_id: (widget, title)},
            detached_module_id=module_id,
            detached_origin_index=index,
            detached_title=title,
            detached_widget=widget,
        )
        detached.setWindowTitle(
            QCoreApplication.translate("App", "Lúmen (Destacado)") + " - " + title
        )
        detached.show()

    except Exception as e:
        logger.error(f"Falha ao destacar aba {index}: {e}", exc_info=True)


def _reattach_module_tab(self, module_id: str, widget, title: str, origin_index: int | None = None) -> None:
    try:
        if not hasattr(self, "tabs"):
            return

        if hasattr(self, "_tab_module_ids") and module_id in self._tab_module_ids:
            return

        tab_order = [
            "leitor_acessivel",
            "gestao_tempo",
            "mapas_mentais",
            "metodo_feynman",
            "matriz_eisenhower",
        ]

        def _order_pos(mid: str) -> int:
            try:
                return tab_order.index(mid)

            except Exception:
                return 10_000

        desired_pos = _order_pos(module_id)
        insert_at = self.tabs.count()
        try:
            for i, mid in enumerate(getattr(self, "_tab_module_ids", []) or []):
                if _order_pos(mid) > desired_pos:
                    insert_at = i
                    break

        except Exception:
            pass

        try:
            if hasattr(self, "_lazy_tabs") and isinstance(self._lazy_tabs, dict):
                new_lazy = {}
                for k, v in self._lazy_tabs.items():
                    if k < insert_at:
                        new_lazy[k] = v

                    else:
                        new_lazy[k + 1] = v

                self._lazy_tabs = new_lazy

        except Exception:
            pass

        try:
            if hasattr(self, "_lazy_tabs") and isinstance(self._lazy_tabs, dict):
                attr_by_id = {
                    "leitor_acessivel": "leitor",
                    "gestao_tempo": "gerenciador",
                    "mapas_mentais": "mapa",
                    "metodo_feynman": "feynman",
                    "matriz_eisenhower": "eisenhower",
                }
                self._lazy_tabs[insert_at] = {
                    "attr": attr_by_id.get(module_id, module_id),
                    "module_id": module_id,
                    "loaded": True,
                }

        except Exception:
            pass

        self.tabs.insertTab(insert_at, widget, title)
        try:
            self._tab_module_ids.insert(insert_at, module_id)

        except Exception:
            pass

        self.tabs.setCurrentIndex(insert_at)

        try:
            from PySide6.QtCore import QCoreApplication

            titles = {
                "leitor_acessivel": QCoreApplication.translate("App", "📖 Leitor Acessível"),
                "gestao_tempo": QCoreApplication.translate("App", "⏱️ Gestão de Tempo"),
                "mapas_mentais": QCoreApplication.translate("App", "🧠 Mapas Mentais"),
                "metodo_feynman": QCoreApplication.translate("App", "🎓 Método Feynman"),
                "matriz_eisenhower": QCoreApplication.translate("App", "🗂️ Matriz Eisenhower"),
            }

            for i in range(self.tabs.count()):
                mid = self._tab_module_ids[i] if i < len(self._tab_module_ids) else None
                if mid in titles:
                    self.tabs.setTabText(i, titles[mid])

        except Exception:
            pass

    except Exception as e:
        logger.error(f"Falha ao reanexar módulo {module_id}: {e}", exc_info=True)
