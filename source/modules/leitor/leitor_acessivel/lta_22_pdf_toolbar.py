from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QSpinBox, QComboBox
from PySide6.QtCore import QCoreApplication
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
        self.btn_last_page.clicked.connect(lambda: self._pdf_goto_page(self.pdf_view.pageCount() - 1 if self.pdf_view else 0))
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

        self.btn_find = QPushButton(QCoreApplication.translate("App", "🔎 Buscar"))
        self.btn_find.clicked.connect(self._pdf_find_show)
        toolbar.addWidget(self.btn_find)

        toolbar.addStretch()

        self.label_mode = QLabel(QCoreApplication.translate("App", "Ferramentas:"))
        toolbar.addWidget(self.label_mode)

        self.btn_mode_select = QPushButton(QCoreApplication.translate("App", "📝 Seleção"))
        self.btn_mode_select.setCheckable(True)
        self.btn_mode_select.setChecked(False)
        self.btn_mode_select.setToolTip(QCoreApplication.translate("App", "Selecionar texto\n(Clique e arraste para selecionar, duplo clique para palavra, triplo para linha)"))
        self.btn_mode_select.clicked.connect(self._pdf_set_selection_mode)
        toolbar.addWidget(self.btn_mode_select)

        self.btn_mode_hand = QPushButton(QCoreApplication.translate("App", "✋ Mão"))
        self.btn_mode_hand.setCheckable(True)
        self.btn_mode_hand.setChecked(False)
        self.btn_mode_hand.setToolTip(QCoreApplication.translate("App", "Arrastar documento\n(Clique e arraste para mover)"))
        self.btn_mode_hand.clicked.connect(self._pdf_set_hand_mode)
        toolbar.addWidget(self.btn_mode_hand)

        self._pdf_toolbar_widgets = [
            self.btn_first_page, self.btn_prev_page, self.btn_next_page,
            self.btn_last_page, self.spin_page, self.btn_zoom_in,
            self.btn_zoom_out, self.btn_zoom_fit_width, self.btn_zoom_fit_page,
            self.combo_zoom, self.btn_mode_hand, self.btn_mode_select, self.btn_find
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

def _pdf_update_page_ui(self, page_index: int, total: int | None = None):
    try:
        self._pdf_current_page = int(page_index)

        if total is None and getattr(self, "pdf_view", None):
            total = self.pdf_view.pageCount()

        if hasattr(self, "spin_page") and self.spin_page is not None:
            self.spin_page.blockSignals(True)
            self.spin_page.setValue(int(page_index) + 1)
            self.spin_page.blockSignals(False)

        if hasattr(self, "label_total_pages") and self.label_total_pages is not None and total is not None:
            self.label_total_pages.setText(f"/ {max(1, int(total))}")

    except Exception as e:
        logger.debug(f"Erro ao atualizar UI de página: {e}", exc_info=True)

def _pdf_next_page(self):
    try:
        if getattr(self, "pdf_view", None):
            current = int(getattr(self, "_pdf_current_page", self.spin_page.value() - 1))
            self._pdf_goto_page(current + 1)

    except Exception as e:
        logger.error(f"Erro ao ir para próxima página: {e}", exc_info=True)

def _pdf_prev_page(self):
    try:
        if getattr(self, "pdf_view", None):
            current = int(getattr(self, "_pdf_current_page", self.spin_page.value() - 1))
            self._pdf_goto_page(current - 1)

    except Exception as e:
        logger.error(f"Erro ao ir para página anterior: {e}", exc_info=True)

def _pdf_goto_page(self, page_num):
    try:
        if not getattr(self, "pdf_view", None):
            return

        total = self.pdf_view.pageCount()
        if 0 <= page_num < total:
            self.pdf_view.goto_page(page_num)
            self._pdf_update_page_ui(page_num, total)

    except Exception as e:
        logger.error(f"Erro ao ir para página {page_num}: {e}", exc_info=True)

def _pdf_zoom_in(self):
    try:
        if getattr(self, "pdf_view", None):
            current = self.pdf_view.zoomFactor()
            new_zoom = min(current * 1.25, 5.0)
            self.pdf_view.setZoomFactor(new_zoom)
            if hasattr(self, "combo_zoom"):
                self.combo_zoom.setCurrentText(f"{int(new_zoom * 100)}%")
                self._pdf_zoom_special = None

    except Exception as e:
        logger.error(f"Erro ao aumentar zoom: {e}", exc_info=True)

def _pdf_zoom_out(self):
    try:
        if getattr(self, "pdf_view", None):
            current = self.pdf_view.zoomFactor()
            new_zoom = max(current / 1.25, 0.25)
            self.pdf_view.setZoomFactor(new_zoom)
            if hasattr(self, "combo_zoom"):
                self.combo_zoom.setCurrentText(f"{int(new_zoom * 100)}%")
                self._pdf_zoom_special = None

    except Exception as e:
        logger.error(f"Erro ao diminuir zoom: {e}", exc_info=True)

def _pdf_zoom_fit_width(self):
    try:
        if getattr(self, "pdf_view", None):
            self._pdf_zoom_special = "largura"
            self.pdf_view.fit_width()

            try:
                z = float(self.pdf_view.zoomFactor())
                if hasattr(self, "combo_zoom"):
                    self.combo_zoom.setCurrentText(f"{int(round(z * 100))}%")

            except Exception:
                pass

            if hasattr(self, "btn_zoom_fit_page"):
                self.btn_zoom_fit_page.setChecked(False)

    except Exception as e:
        logger.error(f"Erro ao ajustar zoom à largura: {e}", exc_info=True)

def _pdf_zoom_fit_page(self):
    try:
        if getattr(self, "pdf_view", None):
            self._pdf_zoom_special = "pagina"
            self.pdf_view.fit_page()

            try:
                z = float(self.pdf_view.zoomFactor())
                if hasattr(self, "combo_zoom"):
                    self.combo_zoom.setCurrentText(f"{int(round(z * 100))}%")

            except Exception:
                pass

            if hasattr(self, "btn_zoom_fit_width"):
                self.btn_zoom_fit_width.setChecked(False)

    except Exception as e:
        logger.error(f"Erro ao ajustar zoom à página: {e}", exc_info=True)

def _pdf_set_hand_mode(self):
    try:
        if not hasattr(self, "btn_mode_hand") or not getattr(self, "_pdf_mouse_handler", None):
            return

        checked = self.btn_mode_hand.isChecked()
        if checked:
            self._pdf_mouse_handler.set_mode("hand")
            self.btn_mode_hand.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")

            if hasattr(self, "btn_mode_select"):
                self.btn_mode_select.setChecked(False)
                self.btn_mode_select.setStyleSheet("")

        else:
            self._pdf_mouse_handler.set_mode("default")
            self.btn_mode_hand.setStyleSheet("")

    except Exception as e:
        logger.error(f"Erro ao alternar modo mão: {e}", exc_info=True)

def _pdf_set_selection_mode(self):
    try:
        if not hasattr(self, "btn_mode_select") or not getattr(self, "_pdf_mouse_handler", None):
            return

        checked = self.btn_mode_select.isChecked()
        if checked:
            self._pdf_mouse_handler.set_mode("select")
            self.btn_mode_select.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

            if hasattr(self, "btn_mode_hand"):
                self.btn_mode_hand.setChecked(False)
                self.btn_mode_hand.setStyleSheet("")

        else:
            self._pdf_mouse_handler.set_mode("default")
            self.btn_mode_select.setStyleSheet("")

    except Exception as e:
        logger.error(f"Erro ao definir modo de seleção do PDF: {e}", exc_info=True)

def _pdf_enable_toolbar(self, enable=True):
    try:
        if hasattr(self, '_pdf_toolbar_widgets'):
            for w in self._pdf_toolbar_widgets:
                w.setEnabled(enable)

        if enable and getattr(self, "pdf_view", None):
            total = self.pdf_view.pageCount()
            self.spin_page.setMaximum(max(1, total))
            self.label_total_pages.setText(f"/ {max(1, total)}")

            self._pdf_update_page_ui(getattr(self.pdf_view, "currentPage", lambda: 0)(), total)

            if not getattr(self, "_pdf_mouse_handler", None):
                try:
                    from .lta_23_pdf_mouse_handler import PDFMouseHandler
                    self._pdf_mouse_handler = PDFMouseHandler(self.pdf_view, owner=self)

                except Exception as e:
                    logger.debug(f"Erro ao criar PDFMouseHandler: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao habilitar toolbar PDF: {e}", exc_info=True)

def _pdf_set_zoom_value(self, text):
    try:
        if not getattr(self, "pdf_view", None):
            return

        s = str(text).strip()
        if not s:
            return

        s_low = s.lower()
        if "largura" in s_low:
            self._pdf_zoom_special = "largura"
            self._pdf_zoom_fit_width()
            return

        if "página" in s_low or "pagina" in s_low:
            self._pdf_zoom_special = "pagina"
            self._pdf_zoom_fit_page()
            return

        s_num = s.replace("%", "").strip()
        val = float(s_num.replace(",", "."))
        new_zoom = max(0.25, min(val / 100.0, 5.0))

        self.pdf_view.setZoomFactor(new_zoom)
        self._pdf_zoom_special = None

        if hasattr(self, "combo_zoom"):
            self.combo_zoom.setCurrentText(f"{int(new_zoom * 100)}%")

        if hasattr(self, "btn_zoom_fit_width"):
            self.btn_zoom_fit_width.setChecked(False)

        if hasattr(self, "btn_zoom_fit_page"):
            self.btn_zoom_fit_page.setChecked(False)

    except Exception as e:
        logger.error(f"Erro ao definir zoom pelo campo: {e}", exc_info=True)
