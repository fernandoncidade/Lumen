import os
import sys
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_app_base_path():
    try:
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                base = sys._MEIPASS
                logger.debug(f"Executando como PyInstaller: {base}")
                return base

            else:
                exe_dir = os.path.dirname(sys.executable)
                logger.debug(f"Executando como executável: {exe_dir}")
                return exe_dir

        else:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            logger.debug(f"Executando em modo desenvolvimento: {base}")
            return base

    except Exception as e:
        logger.error(f"Erro ao obter caminho base do app: {e}", exc_info=True)
        return None

def get_icon_path(icon_name):
    try:
        base_path = get_app_base_path()
        if not base_path:
            logger.error("Caminho base não encontrado")
            return None

        if not os.path.splitext(icon_name)[1]:
            extensions = ['.png', '.ico', '.svg', '.jpg']

        else:
            extensions = ['']

        possible_paths = []
        for ext in extensions:
            icon_with_ext = icon_name + ext if ext else icon_name
            possible_paths.extend([
                os.path.join(base_path, "assets", "icones", icon_with_ext),
                os.path.join(base_path, "source", "assets", "icones", icon_with_ext),
                os.path.join(base_path, "icones", icon_with_ext),
                os.path.join(base_path, "_internal", "icones", icon_with_ext),
                os.path.join(os.path.dirname(__file__), "..", "assets", "icones", icon_with_ext)
            ])

        for icon_path in possible_paths:
            icon_path = os.path.abspath(icon_path)
            if os.path.exists(icon_path):
                file_size = os.path.getsize(icon_path)
                logger.debug(f"✓ Ícone encontrado: {icon_path} ({file_size} bytes)")
                return icon_path

        logger.error(f"✗ Ícone '{icon_name}' NÃO encontrado em nenhum dos {len(possible_paths)} caminhos")
        return None

    except Exception as e:
        logger.error(f"Erro ao obter caminho do ícone '{icon_name}': {e}", exc_info=True)
        return None
