from source.utils.LogManager import LogManager
import os
import json

logger = LogManager.get_logger()

def _carregar_voz_persistente(self):
    try:
        pf = self._get_persist_file()
        if not pf or not os.path.exists(pf):
            return None

        with open(pf, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("voz")

    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Erro ao carregar voz persistente: {e}", exc_info=True)
        return None
