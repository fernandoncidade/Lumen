from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_traducoes_hierarquia(self):
    try:
        tr = QCoreApplication.translate

        from source.modules.mapa.mapamental.mm_24_gerar_mapa_de_hierarquia import (
            _montar_info_associadas,
            _montar_info_folha,
        )

        def _tentar_atualizar_texto_no(no, novo_texto: str):
            try:
                if hasattr(no, "texto"):
                    no.texto = novo_texto

                if hasattr(no, "atualizar_texto") and callable(getattr(no, "atualizar_texto")):
                    no.atualizar_texto(novo_texto)

                elif hasattr(no, "setText") and callable(getattr(no, "setText")):
                    no.setText(novo_texto)

                for attr in ("texto_item", "_texto_item", "text_item", "_text_item"):
                    ti = getattr(no, attr, None)
                    if ti is not None and hasattr(ti, "setPlainText") and callable(getattr(ti, "setPlainText")):
                        ti.setPlainText(novo_texto)
                        break

            except Exception:
                pass

        for no in getattr(self, "nos", []) or []:
            if hasattr(no, "_lumen_hierarquia_payload"):
                hier = getattr(no, "_lumen_hierarquia_payload", None) or {}
                nivel = int(getattr(no, "_lumen_hierarquia_nivel", hier.get("nivel", 0)) or 0)
                tipo_no = getattr(no, "_lumen_hierarquia_tipo", hier.get("tipo", "secao")) or "secao"

                titulo_key = hier.get("titulo_key")
                if titulo_key:
                    _tentar_atualizar_texto_no(no, tr("App", titulo_key))

                no.info_associada = _montar_info_associadas(tr, hier, nivel, tipo_no)
                if hasattr(no, "_badge"):
                    no._badge.setVisible(True)

            elif hasattr(no, "_lumen_ideia_payload"):
                ideia = getattr(no, "_lumen_ideia_payload", None) or {}
                numero = int(getattr(no, "_lumen_ideia_numero", 1) or 1)
                titulo_pai = getattr(no, "_lumen_ideia_parent_title", "") or ""

                no.info_associada = _montar_info_folha(tr, ideia, numero, titulo_pai)
                if hasattr(no, "_badge"):
                    no._badge.setVisible(True)

    except Exception as e:
        logger.error(f"Erro ao atualizar traduções da hierarquia: {e}", exc_info=True)
