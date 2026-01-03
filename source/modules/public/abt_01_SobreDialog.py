from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser, QSizePolicy, QHBoxLayout, QWidget, QTabWidget
from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()


class SobreDialog(QDialog):
    def __init__(
        self,
        parent,
        titulo,
        texto_fixo,
        texto_history,
        detalhes,
        licencas,
        sites_licencas,
        show_history_text=None,
        hide_history_text=None,
        show_details_text=None,
        hide_details_text=None,
        show_licenses_text=None,
        hide_licenses_text=None,
        ok_text=None,
        site_oficial_text=None,
        avisos=None,
        show_notices_text=None,
        hide_notices_text=None,
        Privacy_Policy=None,
        show_privacy_policy_text=None,
        hide_privacy_policy_text=None,
        info_not_available_text="Information not available",
        release_notes=None,
        show_release_notes_text=None,
        hide_release_notes_text=None,
    ):
        super().__init__(parent)
        try:
            self.setWindowTitle(titulo)
            self.setWindowFlags(
                Qt.Window
                | Qt.WindowTitleHint
                | Qt.WindowSystemMenuHint
                | Qt.WindowMinMaxButtonsHint
                | Qt.WindowCloseButtonHint
            )
            self.setModal(False)

            self._info_not_available_text = info_not_available_text
            self._site_oficial_text = site_oficial_text or "Official site"
            self._sites_licencas = (sites_licencas or "").strip()

            layout = QVBoxLayout(self)
            layout.setContentsMargins(15, 4, 15, 8)
            layout.setSpacing(8)

            header_widget = QWidget()
            header_layout = QVBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(0)

            self.fixed_label = QLabel(texto_fixo)
            self.fixed_label.setTextFormat(Qt.TextFormat.RichText)
            self.fixed_label.setWordWrap(True)
            self.fixed_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.fixed_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

            try:
                self.fixed_label.setMargin(0)
                self.fixed_label.setContentsMargins(0, 0, 0, 0)
                self.fixed_label.setStyleSheet("padding:0; margin:0;")

            except Exception:
                pass

            header_layout.addWidget(self.fixed_label)

            header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            header_widget.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(header_widget)

            sh_history = show_history_text or "Histórico"
            hi_history = hide_history_text or "Ocultar histórico"
            sh_details = show_details_text or "Detalhes"
            hi_details = hide_details_text or "Ocultar detalhes"
            sh_licenses = show_licenses_text or "Licenças"
            hi_licenses = hide_licenses_text or "Ocultar licenças"
            sh_notices = show_notices_text or "Avisos"
            hi_notices = hide_notices_text or "Ocultar avisos"
            sh_privacy = show_privacy_policy_text or "Política de privacidade"
            hi_privacy = hide_privacy_policy_text or "Ocultar política de privacidade"
            sh_release = show_release_notes_text or "Notas de versão"
            hi_release = hide_release_notes_text or "Ocultar notas de versão"
            ok_text = ok_text or "OK"

            self.tabs = QTabWidget()
            self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            try:
                self.tabs.setContentsMargins(0, 0, 0, 0)
                self.tabs.setStyleSheet("QTabWidget::pane { margin-top: 0; padding-top: 0; }")

            except Exception:
                pass

            self.history_browser = QTextBrowser()
            self.history_browser.setReadOnly(True)
            self.history_browser.setOpenExternalLinks(True)
            self.tabs.addTab(self.history_browser, sh_history)

            self.detalhes_browser = QTextBrowser()
            self.detalhes_browser.setReadOnly(True)
            self.detalhes_browser.setOpenExternalLinks(True)
            self.tabs.addTab(self.detalhes_browser, sh_details)

            self.licencas_browser = QTextBrowser()
            self.licencas_browser.setReadOnly(True)
            self.licencas_browser.setOpenExternalLinks(True)
            self.tabs.addTab(self.licencas_browser, sh_licenses)

            self.avisos_browser = QTextBrowser()
            self.avisos_browser.setReadOnly(True)
            self.avisos_browser.setOpenExternalLinks(True)
            self.tabs.addTab(self.avisos_browser, sh_notices)

            self.privacidade_browser = QTextBrowser()
            self.privacidade_browser.setReadOnly(True)
            self.privacidade_browser.setOpenExternalLinks(True)
            self.tabs.addTab(self.privacidade_browser, sh_privacy)

            self.release_notes_browser = QTextBrowser()
            self.release_notes_browser.setReadOnly(True)
            self.release_notes_browser.setOpenExternalLinks(True)
            self.tabs.addTab(self.release_notes_browser, sh_release)

            self._tab_show_texts = [sh_history, sh_details, sh_licenses, sh_notices, sh_privacy, sh_release]
            self._tab_hide_texts = [hi_history, hi_details, hi_licenses, hi_notices, hi_privacy, hi_release]

            self.tabs.currentChanged.connect(self._on_tab_changed)
            layout.addWidget(self.tabs)

            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(6)
            self.ok_button = QPushButton(ok_text)
            self.ok_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.ok_button.clicked.connect(self.accept)
            button_layout.addStretch(1)
            button_layout.addWidget(self.ok_button)
            layout.addLayout(button_layout)

            self.setMinimumSize(400, 200)

            self.update_content(
                titulo=titulo,
                texto_fixo=texto_fixo,
                texto_history=texto_history,
                detalhes=detalhes,
                licencas=licencas,
                sites_licencas=sites_licencas,
                ok_text=ok_text,
                site_oficial_text=self._site_oficial_text,
                avisos=avisos,
                Privacy_Policy=Privacy_Policy,
                release_notes=release_notes,
                show_history_text=sh_history,
                hide_history_text=hi_history,
                show_details_text=sh_details,
                hide_details_text=hi_details,
                show_licenses_text=sh_licenses,
                hide_licenses_text=hi_licenses,
                show_notices_text=sh_notices,
                hide_notices_text=hi_notices,
                show_privacy_policy_text=sh_privacy,
                hide_privacy_policy_text=hi_privacy,
                show_release_notes_text=sh_release,
                hide_release_notes_text=hi_release,
                info_not_available_text=info_not_available_text,
            )

        except Exception as e:
            logger.error(f"Erro ao criar dialog sobre: {e}", exc_info=True)

    def update_content(
        self,
        *,
        titulo: str,
        texto_fixo: str,
        texto_history: str | None,
        detalhes: str | None,
        licencas: str | None,
        sites_licencas: str | None,
        ok_text: str | None,
        site_oficial_text: str | None,
        avisos: str | None,
        Privacy_Policy: str | None,
        release_notes: str | None,
        show_history_text: str | None = None,
        hide_history_text: str | None = None,
        show_details_text: str | None = None,
        hide_details_text: str | None = None,
        show_licenses_text: str | None = None,
        hide_licenses_text: str | None = None,
        show_notices_text: str | None = None,
        hide_notices_text: str | None = None,
        show_privacy_policy_text: str | None = None,
        hide_privacy_policy_text: str | None = None,
        show_release_notes_text: str | None = None,
        hide_release_notes_text: str | None = None,
        info_not_available_text: str | None = None,
    ) -> None:
        try:
            self.setWindowTitle(titulo)
            self.fixed_label.setText(texto_fixo)

            self._info_not_available_text = info_not_available_text or self._info_not_available_text
            self._site_oficial_text = site_oficial_text or self._site_oficial_text
            self._sites_licencas = (sites_licencas or "").strip()

            def _set_plain(browser: QTextBrowser, text: str | None) -> None:
                if text:
                    browser.setPlainText(text)

                else:
                    browser.setHtml(f"<p>{self._info_not_available_text}.</p>")

            _set_plain(self.history_browser, texto_history)
            _set_plain(self.detalhes_browser, detalhes)
            _set_plain(self.avisos_browser, avisos)
            _set_plain(self.privacidade_browser, Privacy_Policy)
            _set_plain(self.release_notes_browser, release_notes)

            if licencas:
                texto_html = licencas.replace("\n", "<br>")
                texto_html += f"<br><br><h3>{self._site_oficial_text}</h3><ul>"
                for site in self._sites_licencas.split("\n"):
                    site = site.strip()
                    if site:
                        texto_html += f'<li><a href="{site}">{site}</a></li>'

                texto_html += "</ul>"
                self.licencas_browser.setHtml(texto_html)

            else:
                self.licencas_browser.setHtml(f"<p>{self._info_not_available_text}.</p>")

            if ok_text:
                self.ok_button.setText(ok_text)

            sh_history = show_history_text or self._tab_show_texts[0]
            sh_details = show_details_text or self._tab_show_texts[1]
            sh_licenses = show_licenses_text or self._tab_show_texts[2]
            sh_notices = show_notices_text or self._tab_show_texts[3]
            sh_privacy = show_privacy_policy_text or self._tab_show_texts[4]
            sh_release = show_release_notes_text or self._tab_show_texts[5]

            hi_history = hide_history_text or self._tab_hide_texts[0]
            hi_details = hide_details_text or self._tab_hide_texts[1]
            hi_licenses = hide_licenses_text or self._tab_hide_texts[2]
            hi_notices = hide_notices_text or self._tab_hide_texts[3]
            hi_privacy = hide_privacy_policy_text or self._tab_hide_texts[4]
            hi_release = hide_release_notes_text or self._tab_hide_texts[5]

            self._tab_show_texts = [sh_history, sh_details, sh_licenses, sh_notices, sh_privacy, sh_release]
            self._tab_hide_texts = [hi_history, hi_details, hi_licenses, hi_notices, hi_privacy, hi_release]

            self._update_tab_labels(self.tabs.currentIndex())

        except Exception as e:
            logger.error(f"Erro ao atualizar conteúdo do Sobre em runtime: {e}", exc_info=True)

    def _on_tab_changed(self, index):
        try:
            self._update_tab_labels(index)

        except Exception as e:
            logger.error(f"Erro ao atualizar rótulos das abas: {e}", exc_info=True)

    def _update_tab_labels(self, current_index):
        count = self.tabs.count()
        while len(self._tab_show_texts) < count:
            self._tab_show_texts.append("")

        while len(self._tab_hide_texts) < count:
            self._tab_hide_texts.append("")

        for i in range(count):
            show = self._tab_show_texts[i] or ""
            hide = self._tab_hide_texts[i] or ""
            self.tabs.setTabText(i, hide if i == current_index else show)
