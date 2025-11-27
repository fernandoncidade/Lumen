from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def carregar_vozes(self):
    try:
        try:
            for ac in list(self.menu_vozes.actions()):
                try:
                    self.menu_vozes.removeAction(ac)

                except Exception as e:
                    logger.error(f"Erro ao remover ação do menu de vozes: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Erro ao limpar menu de vozes: {e}", exc_info=True)

        self.actions_vozes = []
        self._map_id_voz_action = {}
        self.combo_vozes = None

        try:
            import asyncio, edge_tts as _edge_tts
            list_fn = getattr(_edge_tts, "list_voices", None)
            edge_voices = asyncio.run(list_fn()) if callable(list_fn) else None

            if isinstance(edge_voices, list):
                filtered = []
                for v in edge_voices:
                    id_raw = (v.get("Id") or v.get("id") or "") if isinstance(v, dict) else ""
                    name_raw = (v.get("Name") or v.get("name") or "") if isinstance(v, dict) else ""
                    is_dragon = "DragonHDLatestNeural" in id_raw or "DragonHDLatestNeural" in name_raw
                    is_dragon_flash = "DragonHDFlashLatestNeural" in id_raw or "DragonHDFlashLatestNeural" in name_raw
                    is_microsoft_server = "Microsoft Server Speech Text to Speech Voice" in id_raw or "Microsoft Server Speech Text to Speech Voice" in name_raw
                    if (is_dragon or is_dragon_flash) and not is_microsoft_server:
                        continue

                    filtered.append(v)

                edge_voices = filtered

        except Exception as e:
            logger.error(f"Erro ao listar vozes do edge_tts: {e}", exc_info=True)
            edge_voices = None

        voz_persistida = None
        try:
            voz_persistida = self._carregar_voz_persistente()

        except Exception as e:
            logger.error(f"Erro ao carregar voz persistente: {e}", exc_info=True)
            voz_persistida = None

        if edge_voices:
            from PySide6.QtWidgets import QWidgetAction, QComboBox
            combo = QComboBox()
            for v in edge_voices:
                nome = v.get("Name") or v.get("name") or ""
                short = v.get("ShortName") or v.get("shortName") or v.get("Id") or nome
                locale = v.get("Locale") or v.get("locale") or ""
                nome_exibicao = f"{nome} ({locale})" if locale else nome
                combo.addItem(nome_exibicao, short)
                self._map_id_voz_action[short] = None

            combo.currentIndexChanged.connect(lambda idx, cb=combo: self.definir_voz(cb.itemData(idx)))
            wa = QWidgetAction(self)
            wa.setDefaultWidget(combo)
            self.menu_vozes.addAction(wa)
            self.combo_vozes = combo
            self._voices_source = 'edge'

            try:
                if voz_persistida:
                    idx_found = -1
                    for i in range(combo.count()):
                        if combo.itemData(i) == voz_persistida or voz_persistida in combo.itemText(i) or combo.itemText(i) in voz_persistida:
                            idx_found = i
                            break

                    if idx_found >= 0:
                        combo.setCurrentIndex(idx_found)
                        if hasattr(self, 'leitor') and self.leitor:
                            self.leitor.definir_voz(combo.itemData(idx_found))

                elif hasattr(self, 'leitor') and self.leitor and self.leitor.voz_id_atual is None and combo.count() > 0:
                    first_id = combo.itemData(0)
                    if first_id:
                        self.leitor.definir_voz(first_id)
                        combo.setCurrentIndex(0)

            except Exception as e:
                logger.error(f"Erro ao definir voz persistente: {e}", exc_info=True)

            return

        import pyttsx3
        from PySide6.QtWidgets import QWidgetAction, QComboBox
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        combo = QComboBox()
        for v in voices:
            nome = v.name
            idioma = getattr(v, 'languages', None)
            if idioma:
                try:
                    lang = idioma[0].decode(errors='ignore').replace('_', '-')
                    nome_exibicao = f"{nome} ({lang})"

                except Exception as e:
                    logger.error(f"Erro ao decodificar idioma da voz: {e}", exc_info=True)
                    nome_exibicao = nome

            else:
                nome_exibicao = nome

            combo.addItem(nome_exibicao, getattr(v, 'id', nome_exibicao))

            try:
                self._map_id_voz_action[getattr(v, 'id', nome_exibicao)] = None

            except Exception as e:
                logger.error(f"Erro ao atualizar mapa de id de voz para ação: {e}", exc_info=True)

        if combo.count() > 0:
            combo.currentIndexChanged.connect(lambda idx, cb=combo: self.definir_voz(cb.itemData(idx)))
            wa = QWidgetAction(self)
            wa.setDefaultWidget(combo)
            self.menu_vozes.addAction(wa)
            self.combo_vozes = combo

        self._voices_source = 'pyttsx3'

        try:
            if voz_persistida:
                idx_found = -1
                for i in range(combo.count()):
                    if combo.itemData(i) == voz_persistida or voz_persistida in combo.itemText(i) or combo.itemText(i) in voz_persistida:
                        idx_found = i
                        break

                if idx_found >= 0:
                    combo.setCurrentIndex(idx_found)
                    if hasattr(self, 'leitor') and self.leitor:
                        self.leitor.definir_voz(combo.itemData(idx_found))

            elif hasattr(self, 'leitor') and self.leitor and self.leitor.voz_id_atual is None and combo.count() > 0:
                try:
                    first_id = combo.itemData(0)
                    self.leitor.definir_voz(first_id)
                    combo.setCurrentIndex(0)

                except Exception as e:
                    logger.error(f"Erro ao definir voz persistente: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Erro ao definir voz persistente: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao carregar vozes TTS: {str(e)}", exc_info=True)
