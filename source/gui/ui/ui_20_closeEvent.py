from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def closeEvent(self, event):
    try:
        try:
            if (
                getattr(self, "detached", False)
                and getattr(self, "detached_origin", None) is not None
                and not getattr(self, "detached_reattached", False)
            ):
                origin = self.detached_origin
                module_id = getattr(self, "detached_module_id", None) or getattr(self, "only_module_ids", [None])[0]
                provided = getattr(self, "provided_tabs", {}) or {}
                if module_id in provided:
                    widget, title = provided[module_id]
                    try:
                        origin_index = getattr(self, "detached_origin_index", None)
                        origin._reattach_module_tab(module_id, widget, title, origin_index=origin_index)

                    except Exception:
                        pass

                event.accept()
                return

        except Exception:
            pass

        if hasattr(self, 'leitor') and self.leitor:
            try:
                self.leitor.cleanup()

            except Exception:
                pass

        if hasattr(self, 'leitor') and self.leitor and hasattr(self.leitor, 'regua') and self.leitor.regua:
            try:
                self.leitor.regua.close()

            except Exception:
                pass

        if hasattr(self, 'gerenciador') and self.gerenciador:
            try:
                if hasattr(self.gerenciador, 'cleanup'):
                    self.gerenciador.cleanup()

            except Exception:
                pass

        try:
            if hasattr(self, 'mapa') and getattr(self, 'mapa'):
                if hasattr(self.mapa, 'cleanup'):
                    try:
                        self.mapa.cleanup()

                    except Exception:
                        pass

        except Exception:
            pass

        event.accept()

    except Exception as e:
        logger.error(f"Erro ao fechar aplicação: {str(e)}", exc_info=True)
        event.accept()
