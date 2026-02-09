from pathlib import Path
from source.utils.LogManager import LogManager
from source.utils.CaminhoPersistenteUtils import obter_caminho_persistente

logger = LogManager.get_logger()

def _get_persist_file(self):
    try:
        base = obter_caminho_persistente()
        if not base:
            return None

        base_path = Path(base)
        return str(base_path / "voz_selecionada.json")

    except (TypeError, OSError) as e:
        logger.error(f"Erro ao obter caminho do arquivo de voz persistente: {e}", exc_info=True)
        return None
