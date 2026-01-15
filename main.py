import sys
import multiprocessing
from source.utils.LogManager import LogManager

LogManager.enable_startup_diagnostics()
LogManager.install_exception_hook()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    from source.src_01_InicializadorMain import iniciar_aplicacao
    sys.exit(iniciar_aplicacao())
