# Scene / View helpers
from .mm_01_drawBackground import drawBackground
from .mm_02_snap import snap
from .mm_03_wheelEvent import wheelEvent
from .mm_04_animate_focus_on import animate_focus_on

# Hierarquia / visibilidade / handlers
from .mm_05_atualizar_visibilidade_linhas import _atualizar_visibilidade_linhas
from .mm_06_instalar_handlers_nos import _instalar_handlers_nos
from .mm_07_aplicar_visibilidade_por_foco import _aplicar_visibilidade_por_foco
from .mm_08_clicar_no_para_expandir_hierarquia import _clicar_no_para_expandir_hierarquia
from .mm_09_habilitar_navegacao_hierarquia import _habilitar_navegacao_hierarquia
from .mm_10_configurar_hierarquia_por_indices import _configurar_hierarquia_por_indices

# UI / ações do usuário
from .mm_11_setup_ui import setup_ui
from .mm_12_atualizar_traducoes import atualizar_traducoes
from .mm_13_adicionar_no import adicionar_no
from .mm_14_toggle_modo_conexao import toggle_modo_conexao
from .mm_15_clicar_no_para_conectar import clicar_no_para_conectar
from .mm_16_mudar_cor import mudar_cor
from .mm_17_salvar_mapa import salvar_mapa
from .mm_18_carregar_mapa import carregar_mapa
from .mm_19_exportar_imagem import exportar_imagem
from .mm_20_limpar_mapa import limpar_mapa

# Tema / eventos
from .mm_21_atualizar_tema import atualizar_tema
from .mm_22_eventFilter import eventFilter

# IA / Documento / Layout
from .mm_23_importar_documento_ia import importar_documento_ia
from .mm_24_gerar_mapa_de_hierarquia import _gerar_mapa_de_hierarquia
from .mm_25_criar_relacoes_ia import _criar_relacoes_ia
from .mm_26_reorganizar_com_ia import reorganizar_com_ia

# Layout em árvore (reorganização)
from .mm_27_obter_conexoes_existentes import _obter_conexoes_existentes
from .mm_28_construir_hierarquia import _construir_hierarquia
from .mm_29_aplicar_layout_arvore import _aplicar_layout_arvore
from .mm_30_calcular_larguras_subarvore import _calcular_larguras_subarvore
from .mm_31_posicionar_no_arvore import _posicionar_no_arvore
from .mm_32_expandir_area_se_necessario import _expandir_area_se_necessario

__all__ = [
    # Scene / View
    "drawBackground",
    "snap",
    "wheelEvent",
    "animate_focus_on",
    # Hierarquia / visibilidade
    "_atualizar_visibilidade_linhas",
    "_instalar_handlers_nos",
    "_aplicar_visibilidade_por_foco",
    "_clicar_no_para_expandir_hierarquia",
    "_habilitar_navegacao_hierarquia",
    "_configurar_hierarquia_por_indices",
    # UI / ações
    "setup_ui",
    "atualizar_traducoes",
    "adicionar_no",
    "toggle_modo_conexao",
    "clicar_no_para_conectar",
    "mudar_cor",
    "salvar_mapa",
    "carregar_mapa",
    "exportar_imagem",
    "limpar_mapa",
    # Tema / eventos
    "atualizar_tema",
    "eventFilter",
    # IA / Documento
    "importar_documento_ia",
    "_gerar_mapa_de_hierarquia",
    "_criar_relacoes_ia",
    "reorganizar_com_ia",
    # Layout árvore
    "_obter_conexoes_existentes",
    "_construir_hierarquia",
    "_aplicar_layout_arvore",
    "_calcular_larguras_subarvore",
    "_posicionar_no_arvore",
    "_expandir_area_se_necessario",
]
