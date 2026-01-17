# Arquivo utilizado para iniciar a aplicação Lúmen.py com logging detalhado de falhas de inicialização
# Usar a linha de comando Nuitka com "--windows-console-mode=force" para ver a saída do console

import sys
import os
import multiprocessing
import traceback
import tempfile
import datetime
import faulthandler

def _startup_log_path() -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(tempfile.gettempdir(), f"Lumen_startup_{ts}.log")

def _write_startup_log(path: str, text: str) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")

    except Exception:
        pass

def _show_fatal_message(title: str, message: str) -> None:
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, message, title, 0x10)

    except Exception:
        pass


if __name__ == '__main__':
    log_path = _startup_log_path()
    _write_startup_log(log_path, "Lúmen - startup log")
    _write_startup_log(log_path, f"argv={sys.argv}")
    _write_startup_log(log_path, f"executable={sys.executable}")
    _write_startup_log(log_path, f"cwd={os.getcwd()}")
    _write_startup_log(log_path, f"sys.path[0:5]={sys.path[0:5]}")

    try:
        fh = open(log_path, "a", encoding="utf-8")
        faulthandler.enable(file=fh, all_threads=True)

    except Exception:
        fh = None

    try:
        qt_debug = os.environ.get("LUMEN_QT_DEBUG", "").lower()
        if qt_debug in ("1", "true", "yes"):
            os.environ["QT_DEBUG_PLUGINS"] = "1"
            _write_startup_log(log_path, "QT_DEBUG_PLUGINS enabled via LUMEN_QT_DEBUG")
            try:
                if fh is not None:
                    try:
                        sys.stdout.flush()

                    except Exception:
                        pass

                    try:
                        sys.stderr.flush()

                    except Exception:
                        pass

                    sys.stdout = fh
                    sys.stderr = fh

            except Exception:
                pass

    except Exception:
        pass

    try:
        multiprocessing.freeze_support()

        from source.src_02_InicializadorMain import iniciar_aplicacao

        sys.exit(iniciar_aplicacao())

    except Exception as e:
        _write_startup_log(log_path, "\n=== FATAL ERROR ===")
        _write_startup_log(log_path, repr(e))
        _write_startup_log(log_path, traceback.format_exc())
        _show_fatal_message(
            "Lúmen - falha ao iniciar",
            "O Lúmen não conseguiu inicializar.\n\n"
            f"Um log foi salvo em:\n{log_path}\n\n"
            "Envie esse arquivo para diagnóstico.",
        )

        raise

    finally:
        try:
            if fh is not None:
                fh.flush()
                fh.close()

        except Exception:
            pass
