from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QSpinBox, QComboBox
from PySide6.QtCore import QPoint, QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def setup_pdf_toolbar(self):
    try:
        toolbar = QHBoxLayout()

        self.btn_first_page = QPushButton(QCoreApplication.translate("App", "⏮️ Primeira"))
        self.btn_first_page.clicked.connect(lambda: self._pdf_goto_page(0))
        toolbar.addWidget(self.btn_first_page)

        self.btn_prev_page = QPushButton(QCoreApplication.translate("App", "◀️ Anterior"))
        self.btn_prev_page.clicked.connect(self._pdf_prev_page)
        toolbar.addWidget(self.btn_prev_page)

        self.label_page = QLabel(QCoreApplication.translate("App", "Página:"))
        toolbar.addWidget(self.label_page)

        self.spin_page = QSpinBox()
        self.spin_page.setMinimum(1)
        self.spin_page.setValue(1)
        self.spin_page.valueChanged.connect(lambda v: self._pdf_goto_page(v - 1))
        toolbar.addWidget(self.spin_page)

        self.label_total_pages = QLabel("/ 1")
        toolbar.addWidget(self.label_total_pages)

        self.btn_next_page = QPushButton(QCoreApplication.translate("App", "▶️ Próxima"))
        self.btn_next_page.clicked.connect(self._pdf_next_page)
        toolbar.addWidget(self.btn_next_page)

        self.btn_last_page = QPushButton(QCoreApplication.translate("App", "⏭️ Última"))
        self.btn_last_page.clicked.connect(lambda: self._pdf_goto_page(self.pdf_doc.pageCount() - 1 if self.pdf_doc else 0))
        toolbar.addWidget(self.btn_last_page)

        toolbar.addStretch()

        self.label_zoom = QLabel(QCoreApplication.translate("App", "Zoom:"))
        toolbar.addWidget(self.label_zoom)

        self.btn_zoom_out = QPushButton("🔍−")
        self.btn_zoom_out.clicked.connect(self._pdf_zoom_out)
        toolbar.addWidget(self.btn_zoom_out)

        self.combo_zoom = QComboBox()
        self.combo_zoom.setEditable(True)
        zoom_items = ["25%", "50%", "75%", "100%", "125%", "150%", "175%", "200%"]
        for it in zoom_items:
            self.combo_zoom.addItem(it)

        self.combo_zoom.setCurrentText("100%")
        self.combo_zoom.setMaximumWidth(90)
        try:
            self.combo_zoom.activated[str].connect(lambda t: _pdf_set_zoom_value(self, t))

        except Exception as e:
            logger.debug(f"Erro ao conectar sinal activated[str] do combo de zoom: {e}", exc_info=True)
            self.combo_zoom.activated.connect(lambda idx: _pdf_set_zoom_value(self, self.combo_zoom.itemText(idx)))

        if self.combo_zoom.lineEdit():
            self.combo_zoom.lineEdit().returnPressed.connect(lambda: _pdf_set_zoom_value(self, self.combo_zoom.currentText()))

        toolbar.addWidget(self.combo_zoom)

        self.btn_zoom_in = QPushButton("🔍+")
        self.btn_zoom_in.clicked.connect(self._pdf_zoom_in)
        toolbar.addWidget(self.btn_zoom_in)

        self.btn_zoom_fit_width = QPushButton(QCoreApplication.translate("App", "📄 Largura"))
        self.btn_zoom_fit_width.setCheckable(True)
        self.btn_zoom_fit_width.setChecked(False)
        self.btn_zoom_fit_width.clicked.connect(self._pdf_zoom_fit_width)
        toolbar.addWidget(self.btn_zoom_fit_width)

        self.btn_zoom_fit_page = QPushButton(QCoreApplication.translate("App", "📃 Página"))
        self.btn_zoom_fit_page.setCheckable(True)
        self.btn_zoom_fit_page.clicked.connect(self._pdf_zoom_fit_page)
        toolbar.addWidget(self.btn_zoom_fit_page)

        toolbar.addStretch()

        self.label_mode = QLabel(QCoreApplication.translate("App", "Ferramentas:"))
        toolbar.addWidget(self.label_mode)

        self.btn_mode_hand = QPushButton(QCoreApplication.translate("App", "✋ Mão"))
        self.btn_mode_hand.setCheckable(True)
        self.btn_mode_hand.setChecked(False)
        self.btn_mode_hand.setToolTip("Arrastar documento\n(Clique e arraste para mover)")
        self.btn_mode_hand.clicked.connect(self._pdf_set_hand_mode)
        toolbar.addWidget(self.btn_mode_hand)

        self._pdf_toolbar_widgets = [
            self.btn_first_page, self.btn_prev_page, self.btn_next_page, 
            self.btn_last_page, self.spin_page, self.btn_zoom_in, 
            self.btn_zoom_out, self.btn_zoom_fit_width, self.btn_zoom_fit_page,
            self.combo_zoom, self.btn_mode_hand
        ]
        for w in self._pdf_toolbar_widgets:
            w.setEnabled(False)

        try:
            self._pdf_scroll_mode = getattr(self, "_pdf_scroll_mode", "continuous")

        except Exception as e:
            logger.debug(f"Erro ao obter modo de rolagem do PDF: {e}", exc_info=True)
            self._pdf_scroll_mode = "continuous"

        self._pdf_mouse_handler = None
        self._pdf_zoom_special = None

        return toolbar

    except Exception as e:
        logger.error(f"Erro ao criar toolbar PDF: {e}", exc_info=True)
        return QHBoxLayout()

def _pdf_goto_page(self, page_num):
    try:
        if not self.pdf_doc or not self.pdf_view:
            return

        total = self.pdf_doc.pageCount()
        if 0 <= page_num < total:
            if hasattr(self.pdf_view, 'pageNavigator'):
                nav = self.pdf_view.pageNavigator()
                if nav and hasattr(nav, 'jump'):
                    nav.jump(page_num, QPoint(0, 0))

            self.spin_page.blockSignals(True)
            self.spin_page.setValue(page_num + 1)
            self.spin_page.blockSignals(False)

    except Exception as e:
        logger.error(f"Erro ao ir para página {page_num}: {e}", exc_info=True)

def _pdf_next_page(self):
    try:
        if self.pdf_doc:
            current = self.spin_page.value() - 1
            self._pdf_goto_page(current + 1)

    except Exception as e:
        logger.error(f"Erro ao ir para próxima página: {e}", exc_info=True)

def _pdf_prev_page(self):
    try:
        if self.pdf_doc:
            current = self.spin_page.value() - 1
            self._pdf_goto_page(current - 1)

    except Exception as e:
        logger.error(f"Erro ao ir para página anterior: {e}", exc_info=True)

def _pdf_zoom_in(self):
    try:
        if self.pdf_view:
            if hasattr(self.pdf_view, 'setZoomMode') and hasattr(self.pdf_view, 'ZoomMode'):
                try:
                    self.pdf_view.setZoomMode(self.pdf_view.ZoomMode.Custom)

                except Exception as e:
                    logger.error(f"Erro ao definir modo de zoom personalizado: {e}", exc_info=True)

            current = self.pdf_view.zoomFactor() if hasattr(self.pdf_view, 'zoomFactor') else 1.0
            new_zoom = min(current * 1.25, 5.0)
            if hasattr(self.pdf_view, 'setZoomFactor'):
                self.pdf_view.setZoomFactor(new_zoom)

            try:
                if hasattr(self, "combo_zoom"):
                    self.combo_zoom.setCurrentText(f"{int(new_zoom * 100)}%")
                    self._pdf_zoom_special = None

            except Exception as e:
                logger.debug(f"Erro ao atualizar texto do combo de zoom: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao aumentar zoom: {e}", exc_info=True)

def _pdf_zoom_out(self):
    try:
        if self.pdf_view:
            if hasattr(self.pdf_view, 'setZoomMode') and hasattr(self.pdf_view, 'ZoomMode'):
                try:
                    self.pdf_view.setZoomMode(self.pdf_view.ZoomMode.Custom)

                except Exception as e:
                    logger.error(f"Erro ao definir modo de zoom personalizado: {e}", exc_info=True)

            current = self.pdf_view.zoomFactor() if hasattr(self.pdf_view, 'zoomFactor') else 1.0
            new_zoom = max(current / 1.25, 0.25)
            if hasattr(self.pdf_view, 'setZoomFactor'):
                self.pdf_view.setZoomFactor(new_zoom)

            try:
                if hasattr(self, "combo_zoom"):
                    self.combo_zoom.setCurrentText(f"{int(new_zoom * 100)}%")
                    self._pdf_zoom_special = None

            except Exception as e:
                logger.debug(f"Erro ao atualizar texto do combo de zoom: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao diminuir zoom: {e}", exc_info=True)

def _pdf_zoom_fit_width(self):
    try:
        if self.pdf_view and hasattr(self.pdf_view, 'setZoomMode'):
            try:
                if hasattr(self.pdf_view, 'ZoomMode'):
                    self.pdf_view.setZoomMode(self.pdf_view.ZoomMode.FitToWidth)

                    try:
                        if hasattr(self, "btn_zoom_fit_width"):
                            self.btn_zoom_fit_width.setChecked(True)

                        if hasattr(self, "btn_zoom_fit_page"):
                            self.btn_zoom_fit_page.setChecked(False)

                    except Exception as e:
                        logger.debug(f"Erro ao atualizar estado dos botões de ajuste: {e}", exc_info=True)

                    try:
                        self._pdf_scroll_mode = "continuous"
                        if hasattr(self, "btn_zoom_fit_page"):
                            self.btn_zoom_fit_page.setChecked(False)

                    except Exception as e:
                        logger.debug(f"Erro ao desmarcar botão de página: {e}", exc_info=True)

                    try:
                        if hasattr(self.pdf_view, "setPageMode") and hasattr(self.pdf_view, "PageMode"):
                            try:
                                self.pdf_view.setPageMode(self.pdf_view.PageMode.MultiPage)

                            except Exception as e:
                                logger.debug(f"Erro ao definir modo de página múltipla: {e}", exc_info=True)
                                try:
                                    self.pdf_view.setPageMode(self.pdf_view.PageMode.Continuous)

                                except Exception as e:
                                    logger.debug(f"Erro ao definir modo contínuo como alternativa: {e}", exc_info=True)

                        elif hasattr(self.pdf_view, "setViewMode") and hasattr(self.pdf_view, "ViewMode"):
                            try:
                                self.pdf_view.setViewMode(self.pdf_view.ViewMode.MultiPage)

                            except Exception as e:
                                logger.debug(f"Erro ao definir modo de visualização múltipla: {e}", exc_info=True)

                    except Exception as e:
                        logger.debug(f"Erro ao definir modo de visualização múltipla (externo): {e}", exc_info=True)

                    try:
                        if getattr(self, "_pdf_mouse_handler", None):
                            self._pdf_mouse_handler.set_mode("default")

                    except Exception as e:
                        logger.debug(f"Erro ao definir modo padrão no mouse handler: {e}", exc_info=True)

                    try:
                        self._pdf_zoom_special = "largura"
                        if hasattr(self, "combo_zoom"):
                            self.combo_zoom.setCurrentText(QCoreApplication.translate("App", "Largura"))

                    except Exception as e:
                        logger.debug(f"Erro ao atualizar texto do combo de zoom: {e}", exc_info=True)

            except Exception as e:
                logger.debug(f"Erro ao ajustar zoom à largura: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao ajustar zoom à largura: {e}", exc_info=True)

def _pdf_zoom_fit_page(self):
    try:
        if self.pdf_view and hasattr(self.pdf_view, 'setZoomMode'):
            try:
                if hasattr(self.pdf_view, 'ZoomMode'):
                    self.pdf_view.setZoomMode(self.pdf_view.ZoomMode.FitInView)
                    try:
                        if hasattr(self, "btn_zoom_fit_page"):
                            self.btn_zoom_fit_page.setChecked(True)

                        if hasattr(self, "btn_zoom_fit_width"):
                            self.btn_zoom_fit_width.setChecked(False)

                    except Exception as e:
                        logger.debug(f"Erro ao atualizar estado dos botões de ajuste: {e}", exc_info=True)

                    try:
                        self._pdf_scroll_mode = "page"
                        if hasattr(self, "btn_zoom_fit_page"):
                            self.btn_zoom_fit_page.setChecked(True)

                    except Exception as e:
                        logger.debug(f"Erro ao definir modo de rolagem para página: {e}", exc_info=True)

                    try:
                        self._pdf_zoom_special = "pagina"
                        if hasattr(self, "combo_zoom"):
                            self.combo_zoom.setCurrentText(QCoreApplication.translate("App", "Página"))

                    except Exception as e:
                        logger.debug(f"Erro ao atualizar texto do combo de zoom: {e}", exc_info=True)

            except Exception as e:
                logger.debug(f"Erro ao ajustar zoom à página: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao ajustar zoom à página: {e}", exc_info=True)

def _pdf_set_selection_mode(self):
    try:
        if self.pdf_view and self._pdf_mouse_handler:
            self._pdf_mouse_handler.set_mode("select")

            self.btn_mode_select.setChecked(True)
            self.btn_mode_hand.setChecked(False)

            self.btn_mode_select.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            self.btn_mode_hand.setStyleSheet("")

            logger.debug("Modo de seleção ativado")

    except Exception as e:
        logger.error(f"Erro ao definir modo de seleção: {e}", exc_info=True)

def _pdf_set_hand_mode(self):
    try:
        if not hasattr(self, "btn_mode_hand") or not self._pdf_mouse_handler:
            return

        checked = self.btn_mode_hand.isChecked()
        try:
            if checked:
                self._pdf_mouse_handler.set_mode("hand")
                self.btn_mode_hand.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
                logger.debug("Modo mão ativado pelo usuário")

            else:
                self._pdf_mouse_handler.set_mode("default")
                self.btn_mode_hand.setStyleSheet("")
                logger.debug("Modo mão desativado pelo usuário (cursor padrão)")

        except Exception as e:
            logger.error(f"Erro ao alternar modo mão: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao definir modo mão: {e}", exc_info=True)

def _pdf_enable_toolbar(self, enable=True):
    try:
        if hasattr(self, '_pdf_toolbar_widgets'):
            for w in self._pdf_toolbar_widgets:
                w.setEnabled(enable)

        if enable and self.pdf_doc:
            total = self.pdf_doc.pageCount()
            self.spin_page.setMaximum(total)
            self.label_total_pages.setText(f"/ {total}")

            if not self._pdf_mouse_handler:
                try:
                    from source.modules.leitor.leitor_acessivel.lta_23_pdf_mouse_handler import PDFMouseHandler
                    self._pdf_mouse_handler = PDFMouseHandler(self.pdf_view, owner=self)
                    logger.debug("PDF Mouse Handler criado com sucesso")

                    try:
                        self._pdf_mouse_handler.set_mode("default")

                    except Exception as e:
                        logger.error(f"Erro ao definir modo padrão no PDF Mouse Handler: {e}", exc_info=True)

                except Exception as e:
                    logger.error(f"Erro ao criar PDF Mouse Handler: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao habilitar toolbar PDF: {e}", exc_info=True)

def _pdf_set_zoom_value(self, text):
    try:
        if isinstance(text, int):
            try:
                text = self.combo_zoom.itemText(text)

            except Exception as e:
                logger.debug(f"Erro ao converter índice de zoom para texto: {e}", exc_info=True)
                text = str(text)

        if not self.pdf_view:
            return

        s = str(text).strip()
        if not s:
            return

        s_low = s.lower()
        if "largura" in s_low:
            try:
                self._pdf_zoom_special = "largura"
                self._pdf_zoom_fit_width()

            except Exception as e:
                logger.debug(f"Erro ao aplicar zoom para largura: {e}", exc_info=True)

            return

        if "página" in s_low or "pagina" in s_low:
            try:
                self._pdf_zoom_special = "pagina"
                self._pdf_zoom_fit_page()

            except Exception as e:
                logger.debug(f"Erro ao aplicar zoom para página: {e}", exc_info=True)

            return

        s_num = s.replace("%", "").strip()
        try:
            val = float(s_num.replace(",", "."))

        except Exception as e:
            logger.debug(f"Valor de zoom inválido fornecido: '{text}': {e}", exc_info=True)
            return

        new_zoom = max(0.25, min(val / 100.0, 5.0))
        try:
            if hasattr(self.pdf_view, 'setZoomMode') and hasattr(self.pdf_view, 'ZoomMode'):
                self.pdf_view.setZoomMode(self.pdf_view.ZoomMode.Custom)

        except Exception as e:
            logger.debug(f"Erro ao definir modo de zoom customizado: {e}", exc_info=True)

        try:
            if hasattr(self.pdf_view, 'setZoomFactor'):
                self.pdf_view.setZoomFactor(new_zoom)

            self._pdf_zoom_special = None

        except Exception as e:
            logger.error(f"Erro ao aplicar fator de zoom: {e}", exc_info=True)
            return

        try:
            if hasattr(self, "combo_zoom"):
                self.combo_zoom.setCurrentText(f"{int(new_zoom * 100)}%")

        except Exception as e:
            logger.debug(f"Erro ao atualizar texto do combo de zoom: {e}", exc_info=True)

        try:
            if hasattr(self, "btn_zoom_fit_width"):
                self.btn_zoom_fit_width.setChecked(False)

            if hasattr(self, "btn_zoom_fit_page"):
                self.btn_zoom_fit_page.setChecked(False)

        except Exception as e:
            logger.debug(f"Erro ao desmarcar botões de ajuste de zoom: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao definir zoom pelo campo: {e}", exc_info=True)
