from source.utils.LogManager import LogManager
import json

logger = LogManager.get_logger()

def _salvar_voz_persistente(self, voz_id):
    try:
        pf = self._get_persist_file()
        if not pf:
            return

        data = {"voz": voz_id}
        with open(pf, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except (OSError, TypeError) as e:
        logger.error(f"Erro ao salvar voz persistente: {e}", exc_info=True)
