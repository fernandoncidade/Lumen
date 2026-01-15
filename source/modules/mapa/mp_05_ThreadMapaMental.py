from PySide6.QtCore import QObject, Signal, Slot
from source.utils.LogManager import LogManager
import concurrent.futures
import atexit
import os
import threading
import traceback
logger = LogManager.get_logger()

_MAX_WORKERS = max(1, (os.cpu_count() or 2) - 1)
_PROCESS_POOL = None
_PROCESS_POOL_LOCK = threading.Lock()


def _get_process_pool() -> concurrent.futures.ProcessPoolExecutor:
    global _PROCESS_POOL
    if _PROCESS_POOL is not None:
        return _PROCESS_POOL

    with _PROCESS_POOL_LOCK:
        if _PROCESS_POOL is None:
            _PROCESS_POOL = concurrent.futures.ProcessPoolExecutor(max_workers=_MAX_WORKERS)

        return _PROCESS_POOL

def _process_reorganize_task(textos):
    try:
        from source.modules.mapa.mp_04_ProcessadorIA import ProcessadorIA as _ProcessadorIA
        proc = _ProcessadorIA()
        texto_completo = ". ".join(textos or [])
        doc = proc.nlp(texto_completo)
        conceitos = proc._extrair_conceitos_tfidf(doc, texto_completo)
        relacoes = proc._identificar_relacoes_avancadas(doc, conceitos)
        return relacoes

    except Exception:
        return []

def _shutdown_process_pool():
    try:
        pool = _PROCESS_POOL
        if pool is not None:
            pool.shutdown(wait=False)

    except Exception:
        pass

atexit.register(_shutdown_process_pool)


class MapasWorker(QObject):
    reorganize_finished = Signal(object, object, object)

    def __init__(self):
        super().__init__()
        self.processador_ia = None
        self._lock = threading.Lock()

    @Slot(list, dict, object)
    def process_reorganize(self, textos, conexoes_existentes, visiveis_idx):
        try:
            future = _get_process_pool().submit(_process_reorganize_task, textos)

            timeout_seconds = 30

            try:
                relacoes = future.result(timeout=timeout_seconds)

            except concurrent.futures.TimeoutError:
                future.cancel()
                logger.error(f"Timeout ao processar reorganize (>{timeout_seconds}s)")
                relacoes = []

            except Exception:
                logger.error(f"Erro no worker de processo:\n{traceback.format_exc()}")
                relacoes = []

            self.reorganize_finished.emit(relacoes, conexoes_existentes, visiveis_idx)

        except Exception:
            logger.error(f"Erro ao processar reorganize:\n{traceback.format_exc()}")
            try:
                self.reorganize_finished.emit([], conexoes_existentes, visiveis_idx)

            except Exception:
                pass
