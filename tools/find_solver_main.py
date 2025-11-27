import sys
from PySide6.QtWidgets import QApplication
from source.utils.LogManager import LogManager
import traceback
import tempfile
import os
import time

logger = LogManager.get_logger()


def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Aprendizagem Acessível para TEA")

        # Hook para detectar quem chama .show() / QDialog.exec() durante startup
        from PySide6.QtWidgets import QWidget, QDialog

        _orig_widget_show = QWidget.show
        _orig_qdialog_exec = getattr(QDialog, "exec", None)

        def _dbg_widget_show(self, *a, **kw):
            try:
                tb = "".join(traceback.format_stack(limit=40))
                info = (
                    f"\n=== SHOW DETECTOR: QWidget.show chamado: {self.__class__.__name__} ===\n"
                    f"Timestamp: {time.time()}\n"
                    f"Stack trace (most recent call last):\n{tb}\n"
                )

                try:
                    print(info, file=sys.stderr)

                except Exception:
                    pass

                try:
                    with open(out_path, "a", encoding="utf-8") as f:
                        f.write(info)

                except Exception:
                    pass

            except Exception:
                pass

            return _orig_widget_show(self, *a, **kw)

        QWidget.show = _dbg_widget_show

        if callable(_orig_qdialog_exec):

            def _dbg_qdialog_exec(self, *a, **kw):
                try:
                    tb = "".join(traceback.format_stack(limit=40))
                    info = (
                        f"\n=== SHOW DETECTOR: QDialog.exec chamado: {self.__class__.__name__} ===\n"
                        f"Timestamp: {time.time()}\n"
                        f"Stack trace (most recent call last):\n{tb}\n"
                    )

                    try:
                        print(info, file=sys.stderr)

                    except Exception:
                        pass

                    try:
                        with open(out_path, "a", encoding="utf-8") as f:
                            f.write(info)

                    except Exception:
                        pass

                except Exception:
                    pass

                return _orig_qdialog_exec(self, *a, **kw)

            QDialog.exec = _dbg_qdialog_exec

        # Detector reforçado: imprime stack da(s) primeiras criações de QWidget
        _count = {"n": 0}
        _orig_init = QWidget.__init__
        out_path = os.path.join(tempfile.gettempdir(), f"qwidget_detect_{int(time.time())}.log")

        def _dbg_qwidget_init(self, *a, **kw):
            try:
                _count["n"] += 1
                tb = "".join(traceback.format_stack(limit=40))
                info = (
                    f"\n=== DETECTOR: QWidget instanciado ({_count['n']}): {self.__class__.__name__} ===\n"
                    f"Timestamp: {time.time()}\n"
                    f"Stack trace (most recent call last):\n{tb}\n"
                )

                # sempre imprimir no stderr para aparecer no console
                try:
                    print(info, file=sys.stderr)

                except Exception:
                    pass

                # também gravar em arquivo temporário para envio
                try:
                    with open(out_path, "a", encoding="utf-8") as f:
                        f.write(info)

                except Exception:
                    pass

            except Exception:
                pass

            return _orig_init(self, *a, **kw)

        QWidget.__init__ = _dbg_qwidget_init

        print(f"DEBUG: detector de QWidget ativo — arquivo de saída: {out_path}", file=sys.stderr)

        # IMPORTAR EstudoAcessivel (depois do hook)
        from source import EstudoAcessivel

        window = EstudoAcessivel()
        window.show()
        exit_code = app.exec()
        logger.debug(f"Aplicação encerrada com código de saída: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar aplicação: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
