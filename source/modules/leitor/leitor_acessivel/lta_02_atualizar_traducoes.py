from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def atualizar_traducoes(self):
    try:
        self.btn_carregar.setText(QCoreApplication.translate("App", "📁 Carregar PDF"))
        self.btn_play.setText(QCoreApplication.translate("App", "▶️ Ler"))
        self._update_pause_button()

        if self.btn_stop is not None:
            self.btn_stop.setText(QCoreApplication.translate("App", "⏹️ Parar"))

        self.label_velocidade_titulo.setText(QCoreApplication.translate("App", "Velocidade:"))
        self.label_volume.setText(QCoreApplication.translate("App", "Volume:"))
        self.label_fonte.setText(QCoreApplication.translate("App", "Fonte:"))

        try:
            if hasattr(self, "btn_new"):
                self.btn_new.setText(QCoreApplication.translate("App", "🆕 Novo"))

            if hasattr(self, "btn_save"):
                self.btn_save.setText(QCoreApplication.translate("App", "💾 Salvar Como"))

            if hasattr(self, "btn_bullets"):
                self.btn_bullets.setText(QCoreApplication.translate("App", "• Marcadores"))

            if hasattr(self, "label_spacing"):
                self.label_spacing.setText(QCoreApplication.translate("App", "Espaçamento:"))

            if hasattr(self, "label_indent"):
                self.label_indent.setText(QCoreApplication.translate("App", "Recuo:"))

            if hasattr(self, "label_margin"):
                self.label_margin.setText(QCoreApplication.translate("App", "Margem:"))

            # atualizar itens do combo de espaçamento (opcional, números não traduzem)
            if hasattr(self, "combo_spacing"):
                # manter valores numéricos; caso queira palavras, descomente/exemplo abaixo:
                # self.combo_spacing.clear()
                # self.combo_spacing.addItems([QCoreApplication.translate("App","1.0"),
                #                              QCoreApplication.translate("App","1.15"),
                #                              QCoreApplication.translate("App","1.5"),
                #                              QCoreApplication.translate("App","2.0")])
                pass

        except Exception as e:
            logger.debug(f"Erro ao atualizar traduções da toolbar de Texto: {e}", exc_info=True)

        if self.btn_regua.isChecked():
            texto_regua = QCoreApplication.translate("App", "📏 Desativar Régua de Foco")

        else:
            texto_regua = QCoreApplication.translate("App", "📏 Ativar Régua de Foco")

        self.gerenciador_botoes.set_button_text(self.btn_regua, texto_regua)

        self.dica_regua.setText(QCoreApplication.translate("App", 
            "💡 Dica: Arraste para mover, clique nas bordas para redimensionar, use setas ↑↓←→ para ajuste fino, ESC para fechar"))

        try:
            if hasattr(self, "btn_first_page"):
                self.btn_first_page.setText(QCoreApplication.translate("App", "⏮️ Primeira"))

            if hasattr(self, "btn_prev_page"):
                self.btn_prev_page.setText(QCoreApplication.translate("App", "◀️ Anterior"))

            if hasattr(self, "label_page"):
                self.label_page.setText(QCoreApplication.translate("App", "Página:"))

            if hasattr(self, "label_total_pages"):
                pass

            if hasattr(self, "btn_next_page"):
                self.btn_next_page.setText(QCoreApplication.translate("App", "▶️ Próxima"))

            if hasattr(self, "btn_last_page"):
                self.btn_last_page.setText(QCoreApplication.translate("App", "⏭️ Última"))

            if hasattr(self, "label_zoom"):
                self.label_zoom.setText(QCoreApplication.translate("App", "Zoom:"))

            if hasattr(self, "btn_zoom_out"):
                self.btn_zoom_out.setText(QCoreApplication.translate("App", "🔍−"))

            if hasattr(self, "btn_zoom_in"):
                self.btn_zoom_in.setText(QCoreApplication.translate("App", "🔍+"))

            if hasattr(self, "combo_zoom"):
                try:
                    tr_largura = QCoreApplication.translate("App", "Largura")
                    tr_pagina = QCoreApplication.translate("App", "Página")
                    special = getattr(self, "_pdf_zoom_special", None)

                    if special == "largura":
                        self.combo_zoom.setCurrentText(tr_largura)

                    elif special == "pagina":
                        self.combo_zoom.setCurrentText(tr_pagina)

                    else:
                        cur = (self.combo_zoom.currentText() or "").strip()
                        cur_low = cur.lower()

                        if cur_low in ("largura", tr_largura.lower()):
                            self.combo_zoom.setCurrentText(tr_largura)

                        elif cur_low in ("página", "pagina", tr_pagina.lower()):
                            self.combo_zoom.setCurrentText(tr_pagina)

                except Exception as e:
                    logger.debug(f"Erro ao atualizar texto do combo_zoom: {e}", exc_info=True)

            if hasattr(self, "btn_zoom_fit_width"):
                self.btn_zoom_fit_width.setText(QCoreApplication.translate("App", "📄 Largura"))

            if hasattr(self, "btn_zoom_fit_page"):
                self.btn_zoom_fit_page.setText(QCoreApplication.translate("App", "📃 Página"))

            if hasattr(self, "btn_mode_hand"):
                self.btn_mode_hand.setText(QCoreApplication.translate("App", "✋ Mão"))
                self.btn_mode_hand.setToolTip(QCoreApplication.translate("App", "Arrastar documento\n(Clique e arraste para mover)"))

            if hasattr(self, "label_mode"):
                self.label_mode.setText(QCoreApplication.translate("App", "Ferramentas:"))

        except Exception as e:
            logger.debug(f"Erro ao atualizar traduções do toolbar PDF: {e}", exc_info=True)

        try:
            if hasattr(self, "_content_stack"):
                self._content_stack.setTabText(0, QCoreApplication.translate("App", "Texto"))
                self._content_stack.setTabText(1, QCoreApplication.translate("App", "PDF"))

        except Exception as e:
            logger.debug(f"Erro ao atualizar nomes das abas: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao atualizar traducoes: {str(e)}", exc_info=True)
