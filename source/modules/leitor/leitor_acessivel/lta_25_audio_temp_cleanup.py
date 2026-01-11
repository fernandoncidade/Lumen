import os
from PySide6.QtCore import QTimer
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _safe_remove(path: str) -> bool:
    try:
        if not path:
            return True

        if os.path.exists(path):
            os.remove(path)

        return True

    except Exception as e:
        logger.debug(f"Falha ao remover arquivo (tentativa): {path} :: {e}", exc_info=True)
        return False

def cleanup_paths_with_retry(self, paths, retries: int = 6, delay_ms: int = 250):
    try:
        if not paths:
            return

        unique = []
        seen = set()
        for p in paths:
            if not p:
                continue

            if p in seen:
                continue

            seen.add(p)
            unique.append(p)

        pending = [p for p in unique if os.path.exists(p)]
        if not pending:
            return

        def _attempt(remaining_retries: int):
            still_pending = []
            for p in list(pending):
                if os.path.exists(p) and not _safe_remove(p):
                    still_pending.append(p)

            pending.clear()
            pending.extend(still_pending)

            if pending and remaining_retries > 0:
                QTimer.singleShot(delay_ms, lambda: _attempt(remaining_retries - 1))

            elif pending:
                logger.debug(f"Alguns arquivos não puderam ser removidos após retries: {pending}")

        _attempt(retries)

    except Exception as e:
        logger.error(f"Erro em cleanup_paths_with_retry: {e}", exc_info=True)

def cleanup_edge_tts_temp_in_outdir(self, remove_mp3: bool = True, remove_part: bool = True):
    try:
        outdir = None
        try:
            t = getattr(self, "tts_thread", None)
            outdir = getattr(t, "outdir", None)

        except Exception:
            outdir = None

        if not outdir or not os.path.isdir(outdir):
            try:
                from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente
                outdir = obter_caminho_persistente()

            except Exception:
                return

        if not outdir or not os.path.isdir(outdir):
            return

        leftovers = []
        try:
            for name in os.listdir(outdir):
                low = name.lower()
                is_tts_file = low.startswith("tts_edge_part_") or low.startswith("tts_edge_ts_")
                if not is_tts_file:
                    continue

                if remove_part and (low.endswith(".part") or low.endswith(".mp3.part")):
                    leftovers.append(os.path.join(outdir, name))
                    continue

                if remove_mp3 and low.endswith(".mp3") and not low.endswith(".mp3.part"):
                    leftovers.append(os.path.join(outdir, name))
                    continue

        except Exception as e:
            logger.debug(f"Falha ao listar diretório de TTS: {outdir} :: {e}", exc_info=True)
            return

        if leftovers:
            logger.debug(f"Arquivos TTS temporários a remover: {leftovers}")
            cleanup_paths_with_retry(self, leftovers)

    except Exception as e:
        logger.error(f"Erro em cleanup_edge_tts_temp_in_outdir: {e}", exc_info=True)

def cleanup_edge_tts_parts_in_outdir(self):
    try:
        cleanup_edge_tts_temp_in_outdir(self, remove_mp3=False, remove_part=True)

    except Exception as e:
        logger.error(f"Erro em cleanup_edge_tts_parts_in_outdir: {e}", exc_info=True)
