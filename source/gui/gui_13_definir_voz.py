from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def definir_voz(self, voz_id):
    try:
        if not (hasattr(self, 'leitor') and self.leitor):
            return

        self.leitor.definir_voz(voz_id)

        try:
            if voz_id:
                self._salvar_voz_persistente(voz_id)

        except Exception:
            pass

        try:
            if hasattr(self, 'combo_vozes') and self.combo_vozes is not None:
                combo = self.combo_vozes
                idx_encontrado = -1
                for i in range(combo.count()):
                    try:
                        if combo.itemData(i) == voz_id or voz_id in combo.itemText(i) or combo.itemText(i) in voz_id:
                            idx_encontrado = i
                            break

                    except Exception:
                        pass

                if idx_encontrado >= 0:
                    combo.setCurrentIndex(idx_encontrado)

        except Exception:
            pass

        for ac in getattr(self, 'actions_vozes', []):
            try:
                ac.setChecked(False)

            except Exception:
                pass

        if hasattr(self, '_map_id_voz_action') and voz_id in self._map_id_voz_action:
            try:
                act = self._map_id_voz_action[voz_id]
                if act:
                    act.setChecked(True)

            except Exception:
                pass

    except Exception as e:
        logger.error(f"Erro ao definir voz: {str(e)}", exc_info=True)
