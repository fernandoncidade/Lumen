from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QPushButton
from source.modules.public import (
    SobreDialog,
    SITE_LICENSES,
    LICENSE_TEXT_PT_BR,
    LICENSE_TEXT_EN_US,
    NOTICE_TEXT_PT_BR,
    NOTICE_TEXT_EN_US,
    ABOUT_TEXT_PT_BR,
    ABOUT_TEXT_EN_US,
    Privacy_Policy_pt_BR,
    Privacy_Policy_en_US,
    History_APP_pt_BR,
    History_APP_en_US,
    RELEASE_NOTES_pt_BR,
    RELEASE_NOTES_en_US,
)
from source.utils.LogManager import LogManager
from pathlib import Path
import html
import os

logger = LogManager.get_logger()

def _tr_multi(key: str) -> str:
    val = QCoreApplication.translate("App", key)
    if val and val != key:
        return val

    val = QCoreApplication.translate("InterfaceGrafica", key)
    return val if val and val != key else key

def exibir_sobre(app):
    try:
        idioma = "pt_BR"
        try:
            if hasattr(app, "gerenciador_traducao") and app.gerenciador_traducao:
                idioma = app.gerenciador_traducao.obter_idioma_atual() or "pt_BR"

        except Exception:
            pass

        textos_sobre = { "pt_BR": ABOUT_TEXT_PT_BR, "en_US": ABOUT_TEXT_EN_US }
        textos_licenca = { "pt_BR": LICENSE_TEXT_PT_BR, "en_US": LICENSE_TEXT_EN_US }
        textos_aviso = { "pt_BR": NOTICE_TEXT_PT_BR, "en_US": NOTICE_TEXT_EN_US }
        textos_privacidade = { "pt_BR": Privacy_Policy_pt_BR, "en_US": Privacy_Policy_en_US }
        history_texts = { "pt_BR": History_APP_pt_BR, "en_US": History_APP_en_US }
        release_notes_texts = { "pt_BR": RELEASE_NOTES_pt_BR, "en_US": RELEASE_NOTES_en_US }

        texto_sobre = textos_sobre.get(idioma, textos_sobre["en_US"])
        texto_licenca = textos_licenca.get(idioma, textos_licenca["en_US"])
        texto_aviso = textos_aviso.get(idioma, textos_aviso["en_US"])
        texto_privacidade = textos_privacidade.get(idioma, textos_privacidade["en_US"])
        texto_history = history_texts.get(idioma, history_texts["en_US"])
        texto_release_notes = release_notes_texts.get(idioma, release_notes_texts["en_US"])

        def _lbl(pt, en):
            return pt if idioma == "pt_BR" else en

        show_history = _tr_multi("show_history")
        if show_history == "show_history":
            show_history = _lbl("Histórico", "History")

        hide_history = _tr_multi("hide_history")
        if hide_history == "hide_history":
            hide_history = _lbl("Ocultar histórico", "Hide history")

        show_details = _tr_multi("show_details")
        if show_details == "show_details":
            show_details = _lbl("Detalhes", "Details")

        hide_details = _tr_multi("hide_details")
        if hide_details == "hide_details":
            hide_details = _lbl("Ocultar detalhes", "Hide details")

        show_licenses = _tr_multi("show_licenses")
        if show_licenses == "show_licenses":
            show_licenses = _lbl("Licenças", "Licenses")

        hide_licenses = _tr_multi("hide_licenses")
        if hide_licenses == "hide_licenses":
            hide_licenses = _lbl("Ocultar licenças", "Hide licenses")

        show_notices = _tr_multi("show_notices")
        if show_notices == "show_notices":
            show_notices = _lbl("Avisos", "Notices")

        hide_notices = _tr_multi("hide_notices")
        if hide_notices == "hide_notices":
            hide_notices = _lbl("Ocultar avisos", "Hide notices")

        show_privacy_policy = _tr_multi("show_privacy_policy")
        if show_privacy_policy == "show_privacy_policy":
            show_privacy_policy = _lbl("Política de privacidade", "Privacy Policy")

        hide_privacy_policy = _tr_multi("hide_privacy_policy")
        if hide_privacy_policy == "hide_privacy_policy":
            hide_privacy_policy = _lbl("Ocultar política de privacidade", "Hide privacy policy")

        show_release_notes = _tr_multi("show_release_notes")
        if show_release_notes == "show_release_notes":
            show_release_notes = _lbl("Notas de versão", "Release Notes")

        hide_release_notes = _tr_multi("hide_release_notes")
        if hide_release_notes == "hide_release_notes":
            hide_release_notes = _lbl("Ocultar notas de versão", "Hide release notes")

        titulo_tr = _tr_multi("Sobre - Lúmen")
        if titulo_tr == "Sobre - Lúmen":
            sobre_txt = _tr_multi("Sobre")
            if sobre_txt == "Sobre":
                sobre_txt = _lbl("Sobre", "About")

            titulo_tr = f"{sobre_txt} - Lúmen"

        version_label = _tr_multi("version")
        if version_label == "version":
            version_label = _lbl("Versão", "Version")

        authors_label = _tr_multi("authors:")
        if authors_label == "authors:":
            authors_label = _lbl("Autores:", "Authors:")

        description_label = _tr_multi("description:")
        if description_label == "description:":
            description_label = _lbl("Descrição:", "Description:")

        description_text = _tr_multi("description_text")
        if description_text == "description_text":
            description_text = _lbl("", "")

        app_title_key = "Lúmen"
        app_title = _tr_multi(app_title_key)
        if app_title == app_title_key:
            app_title = "Lúmen" if idioma == "en_US" else app_title_key

        cabecalho_fixo = (
            f"<h3>{app_title}</h3>"
            f"<p><b>{version_label}</b> 2025.12.31.0</p>"
            f"<p><b>{authors_label}</b> Fernando Nillsson Cidade</p>"
            f"<p><b>{description_label}</b> {description_text}</p>"
        )

        dialog = SobreDialog(
            app,
            titulo=titulo_tr,
            texto_fixo=cabecalho_fixo,
            texto_history=texto_history,
            detalhes=texto_sobre,
            licencas=texto_licenca,
            sites_licencas=SITE_LICENSES,
            show_history_text=show_history,
            hide_history_text=hide_history,
            show_details_text=show_details,
            hide_details_text=hide_details,
            show_licenses_text=show_licenses,
            hide_licenses_text=hide_licenses,
            ok_text=_tr_multi("OK") if _tr_multi("OK") != "OK" else _lbl("OK", "OK"),
            site_oficial_text=_tr_multi("site_oficial") if _tr_multi("site_oficial") != "site_oficial" else _lbl("Site oficial", "Official site"),
            avisos=texto_aviso,
            show_notices_text=show_notices,
            hide_notices_text=hide_notices,
            Privacy_Policy=texto_privacidade,
            show_privacy_policy_text=show_privacy_policy,
            hide_privacy_policy_text=hide_privacy_policy,
            info_not_available_text=_tr_multi("information_not_available") if _tr_multi("information_not_available") != "information_not_available" else _lbl("Informação não disponível", "Information not available"),
            release_notes=texto_release_notes,
            show_release_notes_text=show_release_notes,
            hide_release_notes_text=hide_release_notes
        )
        tamanho_base_largura = 900
        tamanho_base_altura = 500
        largura_dialog = int(tamanho_base_largura * 1)
        altura_dialog = int(tamanho_base_altura * 1.2)
        dialog.resize(largura_dialog, altura_dialog)
        dialog.show()

    except Exception as e:
        logger.error(f"Erro ao exibir diálogo Sobre: {e}", exc_info=True)
        QMessageBox.critical(app, _tr_multi("Erro") if _tr_multi("Erro") != "Erro" else "Erro", f"{_tr_multi('Erro') if _tr_multi('Erro') != 'Erro' else 'Erro'}: {e}")

def exibir_manual(app):
    try:
        base_dir = Path(__file__).resolve().parents[2]
        manual_path = base_dir / "MANUAL.md"
        if not manual_path.exists():
            raise FileNotFoundError(f"MANUAL.md não encontrado em: {manual_path}")

        text = manual_path.read_text(encoding="utf-8")
        html_body = None

        try:
            from markdown_it import MarkdownIt
            try:
                from mdit_py_plugins import plugin_gfm
                md = MarkdownIt("commonmark").use(plugin_gfm.gfm_plugin)

            except Exception:
                md = MarkdownIt("commonmark")

            html_body = md.render(text)
            logger.info("Renderizado MANUAL.md via markdown-it-py")

        except Exception as e:
            logger.debug(f"markdown-it-py não disponível ou falha: {e}")

        if not html_body:
            try:
                import markdown
                extensions = ["extra", "codehilite", "tables", "toc", "attr_list", "sane_lists"]
                html_body = markdown.markdown(text, extensions=extensions, output_format="html5")
                logger.info("Renderizado MANUAL.md via python-markdown com extensões")

            except Exception as e:
                logger.error(f"Falha ao converter markdown com python-markdown: {e}", exc_info=True)
                html_body = f"<pre>{html.escape(text)}</pre>"

        github_css = """
        .markdown-body {
          box-sizing: border-box;
          min-width: 200px;
          max-width: 980px;
          margin: 0 auto;
          padding: 30px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
          color: #24292e;
          background: #ffffff;
        }
        body { background-color: #ffffff !important; }
        html { background-color: #ffffff !important; }
        .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 {
          border-bottom: 1px solid #eaecef;
          padding-bottom: .3em;
        }
        .markdown-body pre {
          background: #0d1117;
          color: #c9d1d9;
          padding: 16px;
          overflow: auto;
          border-radius: 6px;
        }
        .markdown-body code {
          background-color: rgba(27,31,35,.05);
          padding: .2em .4em;
          margin: 0;
          font-size: 85%;
          border-radius: 6px;
        }
        .markdown-body table {
          border-collapse: collapse;
        }
        .markdown-body table, .markdown-body th, .markdown-body td {
          border: 1px solid #dfe2e5;
          padding: 6px 13px;
        }
        details summary { cursor: pointer; }
        .center { text-align: center; }
        """

        force_white_bg_js = """
        function setWhiteBg() {
            document.body.style.background = '#ffffff';
            document.documentElement.style.background = '#ffffff';
        }
        setWhiteBg();
        var observer = new MutationObserver(function(mutations) {
            setWhiteBg();
        });
        observer.observe(document.body, { attributes: true, childList: true, subtree: true });
        document.addEventListener('click', function(e) {
            if (e.target && e.target.tagName === 'SUMMARY') {
                setTimeout(setWhiteBg, 10);
            }
        });
        """

        full_html = f"""<!doctype html>
        <html>
        <head>
          <meta charset="utf-8"/>
          <meta name="viewport" content="width=device-width, initial-scale=1"/>
          <style>{github_css}</style>
        </head>
        <body class="markdown-body">
        {html_body}
        <script>{force_white_bg_js}</script>
        </body>
        </html>
        """

        dlg = QDialog()
        dlg.setWindowTitle(_tr_multi("Manual") if _tr_multi("Manual") != "Manual" else "Manual")
        dlg.setMinimumSize(800, 600)
        from PySide6.QtCore import Qt
        dlg.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dlg)

        web_view_added = False
        view = None

        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QColor
            view = QWebEngineView()

            try:
                view.page().setBackgroundColor(QColor("#ffffff"))

            except Exception:
                pass

            view.setHtml(full_html, QUrl.fromLocalFile(str(manual_path.parent) + os.sep))

            def on_load_finished(ok):
                view.page().setBackgroundColor(QColor("#ffffff"))
                view.repaint()

            view.loadFinished.connect(on_load_finished)

            layout.addWidget(view)
            web_view_added = True
            logger.info("Exibindo MANUAL.md via QWebEngineView")

        except Exception as e:
            logger.debug(f"QWebEngineView não disponível ou falha: {e}")

        if not web_view_added:
            from PySide6.QtWidgets import QTextBrowser
            from PySide6.QtCore import QUrl
            browser = QTextBrowser()
            browser.setStyleSheet("background-color: white;")
            browser.setOpenExternalLinks(True)
            browser.setHtml(full_html, QUrl.fromLocalFile(str(manual_path.parent) + os.sep))
            layout.addWidget(browser)
            logger.info("Exibindo MANUAL.md via QTextBrowser (fallback)")

        btn_close = QPushButton(_tr_multi("Fechar") if _tr_multi("Fechar") != "Fechar" else "Fechar")
        from PySide6.QtWidgets import QSizePolicy
        btn_close.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_close.clicked.connect(dlg.accept)
        layout.addWidget(btn_close)

        dlg.setLayout(layout)

        if view is not None:
            class ManualDialog(QDialog):
                def showEvent(self, event):
                    super().showEvent(event)
                    view.setHtml(full_html, QUrl.fromLocalFile(str(manual_path.parent) + os.sep))

                def resizeEvent(self, event):
                    super().resizeEvent(event)
                    if self.isMaximized():
                        view.setHtml(full_html, QUrl.fromLocalFile(str(manual_path.parent) + os.sep))

            manual_dlg = ManualDialog()
            manual_dlg.setWindowTitle(dlg.windowTitle())
            manual_dlg.setMinimumSize(800, 600)
            manual_dlg.setWindowFlags(dlg.windowFlags())
            manual_dlg.setLayout(layout)

            try:
                btn_close.clicked.connect(manual_dlg.accept)

            except Exception:
                pass

            manual_dlg.exec()

        else:
            dlg.exec()

    except Exception as e:
        logger.error(f"Erro ao abrir Manual: {e}", exc_info=True)
        QMessageBox.critical(app, _tr_multi("Erro") if _tr_multi("Erro") != "Erro" else "Erro", f"{_tr_multi('Erro') if _tr_multi('Erro') != 'Erro' else 'Erro'}: {e}")
