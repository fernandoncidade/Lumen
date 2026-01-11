from PySide6.QtCore import QCoreApplication, Qt, QEvent
from PySide6.QtGui import QTextCharFormat, QFont, QTextCursor, QFontMetrics
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QListWidget, QTextBrowser
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
logger = LogManager.get_logger()


def _tr_multi(key: str) -> str:
    val = QCoreApplication.translate("App", key)
    if val and val != key:
        return val

    val = QCoreApplication.translate("InterfaceGrafica", key)
    return val if val and val != key else key


def exibir_sobre(app):
    try:
        existing = getattr(app, "_sobre_dialog", None)
        if existing is not None:
            try:
                if existing.isVisible():
                    existing.raise_()
                    existing.activateWindow()
                    return

            except Exception:
                pass

        def _get_idioma_atual() -> str:
            idioma_local = "pt_BR"
            try:
                if hasattr(app, "gerenciador_traducao") and app.gerenciador_traducao:
                    idioma_local = app.gerenciador_traducao.obter_idioma_atual() or "pt_BR"

            except Exception:
                pass

            return idioma_local

        def _lbl(pt, en, idioma_local: str):
            return pt if idioma_local == "pt_BR" else en

        def _compute_payload(idioma_local: str) -> dict:
            textos_sobre = {"pt_BR": ABOUT_TEXT_PT_BR, "en_US": ABOUT_TEXT_EN_US}
            textos_licenca = {"pt_BR": LICENSE_TEXT_PT_BR, "en_US": LICENSE_TEXT_EN_US}
            textos_aviso = {"pt_BR": NOTICE_TEXT_PT_BR, "en_US": NOTICE_TEXT_EN_US}
            textos_privacidade = {"pt_BR": Privacy_Policy_pt_BR, "en_US": Privacy_Policy_en_US}
            history_texts = {"pt_BR": History_APP_pt_BR, "en_US": History_APP_en_US}
            release_notes_texts = {"pt_BR": RELEASE_NOTES_pt_BR, "en_US": RELEASE_NOTES_en_US}

            texto_sobre = textos_sobre.get(idioma_local, textos_sobre["en_US"])
            texto_licenca = textos_licenca.get(idioma_local, textos_licenca["en_US"])
            texto_aviso = textos_aviso.get(idioma_local, textos_aviso["en_US"])
            texto_privacidade = textos_privacidade.get(idioma_local, textos_privacidade["en_US"])
            texto_history = history_texts.get(idioma_local, history_texts["en_US"])
            texto_release_notes = release_notes_texts.get(idioma_local, release_notes_texts["en_US"])

            show_history = _tr_multi("show_history")
            if show_history == "show_history":
                show_history = _lbl("Histórico", "History", idioma_local)

            hide_history = _tr_multi("hide_history")
            if hide_history == "hide_history":
                hide_history = _lbl("Ocultar histórico", "Hide history", idioma_local)

            show_details = _tr_multi("show_details")
            if show_details == "show_details":
                show_details = _lbl("Detalhes", "Details", idioma_local)

            hide_details = _tr_multi("hide_details")
            if hide_details == "hide_details":
                hide_details = _lbl("Ocultar detalhes", "Hide details", idioma_local)

            show_licenses = _tr_multi("show_licenses")
            if show_licenses == "show_licenses":
                show_licenses = _lbl("Licenças", "Licenses", idioma_local)

            hide_licenses = _tr_multi("hide_licenses")
            if hide_licenses == "hide_licenses":
                hide_licenses = _lbl("Ocultar licenças", "Hide licenses", idioma_local)

            show_notices = _tr_multi("show_notices")
            if show_notices == "show_notices":
                show_notices = _lbl("Avisos", "Notices", idioma_local)

            hide_notices = _tr_multi("hide_notices")
            if hide_notices == "hide_notices":
                hide_notices = _lbl("Ocultar avisos", "Hide notices", idioma_local)

            show_privacy_policy = _tr_multi("show_privacy_policy")
            if show_privacy_policy == "show_privacy_policy":
                show_privacy_policy = _lbl("Política de privacidade", "Privacy Policy", idioma_local)

            hide_privacy_policy = _tr_multi("hide_privacy_policy")
            if hide_privacy_policy == "hide_privacy_policy":
                hide_privacy_policy = _lbl("Ocultar política de privacidade", "Hide privacy policy", idioma_local)

            show_release_notes = _tr_multi("show_release_notes")
            if show_release_notes == "show_release_notes":
                show_release_notes = _lbl("Notas de versão", "Release Notes", idioma_local)

            hide_release_notes = _tr_multi("hide_release_notes")
            if hide_release_notes == "hide_release_notes":
                hide_release_notes = _lbl("Ocultar notas de versão", "Hide release notes", idioma_local)

            titulo_tr = _tr_multi("Sobre - Lúmen")
            if titulo_tr == "Sobre - Lúmen":
                sobre_txt = _tr_multi("Sobre")
                if sobre_txt == "Sobre":
                    sobre_txt = _lbl("Sobre", "About", idioma_local)

                titulo_tr = f"{sobre_txt} - Lúmen"

            version_label = _tr_multi("version")
            if version_label == "version":
                version_label = _lbl("Versão", "Version", idioma_local)

            authors_label = _tr_multi("authors:")
            if authors_label == "authors:":
                authors_label = _lbl("Autores:", "Authors:", idioma_local)

            description_label = _tr_multi("description:")
            if description_label == "description:":
                description_label = _lbl("Descrição:", "Description:", idioma_local)

            description_text = _tr_multi("description_text")
            if description_text == "description_text":
                description_text = _lbl("", "", idioma_local)

            app_title_key = "Lúmen"
            app_title = _tr_multi(app_title_key)
            if app_title == app_title_key:
                app_title = "Lúmen" if idioma_local == "en_US" else app_title_key

            cabecalho_fixo = (
                f"<h3>{app_title}</h3>"
                f"<p><b>{version_label}</b> 2026.1.11.0</p>"
                f"<p><b>{authors_label}</b> Fernando Nillsson Cidade</p>"
                f"<p><b>{description_label}</b> {description_text}</p>"
            )

            ok_text = _tr_multi("OK")
            if ok_text == "OK":
                ok_text = _lbl("OK", "OK", idioma_local)

            site_oficial_text = _tr_multi("site_oficial")
            if site_oficial_text == "site_oficial":
                site_oficial_text = _lbl("Site oficial", "Official site", idioma_local)

            info_not_available_text = _tr_multi("information_not_available")
            if info_not_available_text == "information_not_available":
                info_not_available_text = _lbl("Informação não disponível", "Information not available", idioma_local)

            return {
                "titulo": titulo_tr,
                "texto_fixo": cabecalho_fixo,
                "texto_history": texto_history,
                "detalhes": texto_sobre,
                "licencas": texto_licenca,
                "sites_licencas": SITE_LICENSES,
                "show_history_text": show_history,
                "hide_history_text": hide_history,
                "show_details_text": show_details,
                "hide_details_text": hide_details,
                "show_licenses_text": show_licenses,
                "hide_licenses_text": hide_licenses,
                "ok_text": ok_text,
                "site_oficial_text": site_oficial_text,
                "avisos": texto_aviso,
                "show_notices_text": show_notices,
                "hide_notices_text": hide_notices,
                "Privacy_Policy": texto_privacidade,
                "show_privacy_policy_text": show_privacy_policy,
                "hide_privacy_policy_text": hide_privacy_policy,
                "info_not_available_text": info_not_available_text,
                "release_notes": texto_release_notes,
                "show_release_notes_text": show_release_notes,
                "hide_release_notes_text": hide_release_notes,
            }

        def refresh_sobre() -> None:
            idioma_local = _get_idioma_atual()
            p = _compute_payload(idioma_local)
            dialog.update_content(
                titulo=p["titulo"],
                texto_fixo=p["texto_fixo"],
                texto_history=p["texto_history"],
                detalhes=p["detalhes"],
                licencas=p["licencas"],
                sites_licencas=p["sites_licencas"],
                ok_text=p["ok_text"],
                site_oficial_text=p["site_oficial_text"],
                avisos=p["avisos"],
                Privacy_Policy=p["Privacy_Policy"],
                release_notes=p["release_notes"],
                show_history_text=p["show_history_text"],
                hide_history_text=p["hide_history_text"],
                show_details_text=p["show_details_text"],
                hide_details_text=p["hide_details_text"],
                show_licenses_text=p["show_licenses_text"],
                hide_licenses_text=p["hide_licenses_text"],
                show_notices_text=p["show_notices_text"],
                hide_notices_text=p["hide_notices_text"],
                show_privacy_policy_text=p["show_privacy_policy_text"],
                hide_privacy_policy_text=p["hide_privacy_policy_text"],
                show_release_notes_text=p["show_release_notes_text"],
                hide_release_notes_text=p["hide_release_notes_text"],
                info_not_available_text=p["info_not_available_text"],
            )


        class SobreDialogRuntime(SobreDialog):
            def changeEvent(self, event) -> None:
                super().changeEvent(event)
                if event.type() == QEvent.Type.LanguageChange:
                    try:
                        refresh_sobre()

                    except Exception:
                        logger.debug("Falha ao atualizar tradução do Sobre em runtime", exc_info=True)

        idioma = _get_idioma_atual()
        p = _compute_payload(idioma)

        dialog = SobreDialogRuntime(
            None,
            titulo=p["titulo"],
            texto_fixo=p["texto_fixo"],
            texto_history=p["texto_history"],
            detalhes=p["detalhes"],
            licencas=p["licencas"],
            sites_licencas=p["sites_licencas"],
            show_history_text=p["show_history_text"],
            hide_history_text=p["hide_history_text"],
            show_details_text=p["show_details_text"],
            hide_details_text=p["hide_details_text"],
            show_licenses_text=p["show_licenses_text"],
            hide_licenses_text=p["hide_licenses_text"],
            ok_text=p["ok_text"],
            site_oficial_text=p["site_oficial_text"],
            avisos=p["avisos"],
            show_notices_text=p["show_notices_text"],
            hide_notices_text=p["hide_notices_text"],
            Privacy_Policy=p["Privacy_Policy"],
            show_privacy_policy_text=p["show_privacy_policy_text"],
            hide_privacy_policy_text=p["hide_privacy_policy_text"],
            info_not_available_text=p["info_not_available_text"],
            release_notes=p["release_notes"],
            show_release_notes_text=p["show_release_notes_text"],
            hide_release_notes_text=p["hide_release_notes_text"],
        )

        setattr(app, "_sobre_dialog", dialog)

        def _clear_sobre_dialog(*_args) -> None:
            if getattr(app, "_sobre_dialog", None) is dialog:
                setattr(app, "_sobre_dialog", None)

        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dialog.destroyed.connect(_clear_sobre_dialog)

        qt_app = QCoreApplication.instance()
        if qt_app is not None:
            qt_app.aboutToQuit.connect(dialog.close)

        try:
            app.destroyed.connect(dialog.close)

        except Exception:
            pass

        dialog.resize(900, int(500 * 1.2))
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    except Exception as e:
        logger.error(f"Erro ao exibir diálogo Sobre: {e}", exc_info=True)
        QMessageBox.critical(
            app,
            _tr_multi("Erro") if _tr_multi("Erro") != "Erro" else "Erro",
            f"{_tr_multi('Erro') if _tr_multi('Erro') != 'Erro' else 'Erro'}: {e}",
        )


def exibir_manual(app):
    try:
        existing = getattr(app, "_manual_dialog", None)
        if existing is not None:
            try:
                if existing.isVisible():
                    existing.raise_()
                    existing.activateWindow()
                    return

            except Exception:
                pass

        def _get_idioma_atual() -> str:
            idioma_local = "pt_BR"
            try:
                if hasattr(app, "gerenciador_traducao") and app.gerenciador_traducao:
                    idioma_local = app.gerenciador_traducao.obter_idioma_atual() or "pt_BR"

            except Exception:
                pass

            return idioma_local

        from source.modules.public.abt_03_Manual import (get_manual_blocks, get_manual_document, get_manual_title,)

        idioma = _get_idioma_atual()
        window_title = get_manual_title(idioma)
        blocks, order = get_manual_blocks(idioma)
        sections = get_manual_document(idioma)


        class ManualDialog(QDialog):
            def changeEvent(self, event) -> None:
                super().changeEvent(event)
                if event.type() == QEvent.Type.LanguageChange:
                    try:
                        refresh_manual()

                    except Exception:
                        logger.debug("Falha ao atualizar tradução do Manual em runtime", exc_info=True)

        dlg = ManualDialog()
        dlg.setWindowTitle(window_title)

        dlg.setWindowFlags(
            dlg.windowFlags()
            | Qt.WindowType.Window
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        dlg.setWindowModality(Qt.WindowModality.NonModal)
        dlg.setModal(False)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        setattr(app, "_manual_dialog", dlg)

        def _clear_manual_dialog(*_args) -> None:
            if getattr(app, "_manual_dialog", None) is dlg:
                setattr(app, "_manual_dialog", None)

        dlg.destroyed.connect(_clear_manual_dialog)

        qt_app = QCoreApplication.instance()
        if qt_app is not None:
            qt_app.aboutToQuit.connect(dlg.close)

        try:
            app.destroyed.connect(dlg.close)

        except Exception:
            pass

        dlg.setMinimumSize(900, 650)

        root = QVBoxLayout(dlg)

        body = QHBoxLayout()
        root.addLayout(body)

        lst = QListWidget()
        lst.setMinimumWidth(300)

        viewer = QTextBrowser()
        viewer.setReadOnly(True)
        viewer.setOpenLinks(False)

        body.addWidget(lst, 0)
        body.addWidget(viewer, 1)

        btn_close = QPushButton()
        btn_close.clicked.connect(dlg.close)
        root.addWidget(btn_close)

        dlg._manual_positions = {}
        dlg._manual_row_to_id = []
        dlg._manual_id_to_title = {}

        def _apply_close_label() -> None:
            close_text = _tr_multi("Fechar")
            if close_text == "Fechar":
                close_text = "Fechar" if _get_idioma_atual() == "pt_BR" else "Close"

            btn_close.setText(close_text)

            fm = QFontMetrics(btn_close.font())
            text_w = fm.horizontalAdvance(btn_close.text())
            btn_close.setFixedWidth(text_w + 24)

        def _render_manual(lang: str) -> None:
            nonlocal blocks, order, sections

            blocks, order = get_manual_blocks(lang)
            sections = get_manual_document(lang)

            dlg._manual_id_to_title = {s.id: s.title for s in sections}
            dlg._manual_row_to_id = list(order)

            lst.blockSignals(True)
            lst.clear()
            for sid in dlg._manual_row_to_id:
                lst.addItem(dlg._manual_id_to_title.get(sid, sid))

            lst.blockSignals(False)

            viewer.clear()

            base_font = viewer.font()
            base_size = base_font.pointSize()
            if base_size is None or base_size <= 0:
                base_size = 10

            fmt_normal = QTextCharFormat()
            fmt_normal.setFont(base_font)

            fmt_main_title = QTextCharFormat(fmt_normal)
            fmt_main_title.setFontWeight(QFont.Weight.Bold)
            fmt_main_title.setFontPointSize(base_size + 8)

            fmt_toc_title = QTextCharFormat(fmt_normal)
            fmt_toc_title.setFontWeight(QFont.Weight.Bold)

            fmt_toc_item = QTextCharFormat(fmt_normal)
            fmt_toc_item.setFontWeight(QFont.Weight.Bold)

            fmt_body_title = QTextCharFormat(fmt_normal)
            fmt_body_title.setFontWeight(QFont.Weight.Bold)
            fmt_body_title.setFontPointSize(base_size + 2)

            cursor = viewer.textCursor()
            cursor.beginEditBlock()

            dlg._manual_positions = {}

            def insert_line(text: str, fmt: QTextCharFormat | None = None) -> None:
                cursor.insertText(text, fmt or fmt_normal)
                cursor.insertBlock()

            def insert_blank() -> None:
                cursor.insertBlock()

            manual_title = get_manual_title(lang)
            title_line_used = False

            for blk in blocks:
                if blk.kind == "blank":
                    insert_blank()
                    continue

                if blk.kind == "divider":
                    insert_line(blk.text, fmt_normal)
                    continue

                if blk.kind == "toc_title":
                    insert_line(blk.text, fmt_toc_title)
                    continue

                if blk.kind == "toc_item":
                    fmt_link = QTextCharFormat(fmt_toc_item)
                    fmt_link.setAnchor(True)
                    fmt_link.setAnchorHref(blk.section_id or "")
                    insert_line(blk.text, fmt_link)
                    continue

                if blk.kind in ("section_title", "detail_title"):
                    if blk.section_id:
                        dlg._manual_positions[blk.section_id] = cursor.position()

                    insert_line(blk.text, fmt_body_title)
                    continue

                if blk.kind == "bullet":
                    insert_line(f"- {blk.text}", fmt_normal)
                    continue

                if blk.kind == "line":
                    if (not title_line_used) and (blk.text == manual_title):
                        insert_line(blk.text, fmt_main_title)
                        title_line_used = True

                    else:
                        insert_line(blk.text, fmt_normal)

                    continue

                insert_line(blk.text, fmt_normal)

            cursor.endEditBlock()
            viewer.moveCursor(QTextCursor.Start)

        def scroll_cursor_to_top() -> None:
            viewer.ensureCursorVisible()
            sb = viewer.verticalScrollBar()
            y = viewer.cursorRect().top()
            sb.setValue(sb.value() + y)

        def go_to_section_id(section_id: str) -> None:
            try:
                pos = getattr(dlg, "_manual_positions", {}).get(section_id)
                if pos is None:
                    return

                c = viewer.textCursor()
                c.setPosition(pos)
                viewer.setTextCursor(c)
                scroll_cursor_to_top()

            except Exception:
                logger.debug("Falha ao navegar para seção do manual", exc_info=True)

        def go_to_section(row: int) -> None:
            ids = getattr(dlg, "_manual_row_to_id", [])
            if row < 0 or row >= len(ids):
                return

            go_to_section_id(ids[row])

        def on_anchor_clicked(url) -> None:
            sid = url.toString().strip()
            if not sid:
                return

            go_to_section_id(sid)

        def refresh_manual() -> None:
            ids = getattr(dlg, "_manual_row_to_id", [])
            current_row = lst.currentRow()
            current_sid = ids[current_row] if 0 <= current_row < len(ids) else None

            lang = _get_idioma_atual()
            dlg.setWindowTitle(get_manual_title(lang))
            _apply_close_label()
            _render_manual(lang)

            if current_sid and current_sid in dlg._manual_row_to_id:
                lst.setCurrentRow(dlg._manual_row_to_id.index(current_sid))

            else:
                lst.setCurrentRow(0)

        viewer.anchorClicked.connect(on_anchor_clicked)
        lst.currentRowChanged.connect(go_to_section)

        _apply_close_label()
        _render_manual(idioma)
        lst.setCurrentRow(0)

        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    except Exception as e:
        logger.error(f"Erro ao abrir Manual: {e}", exc_info=True)
        QMessageBox.critical(
            app,
            _tr_multi("Erro") if _tr_multi("Erro") != "Erro" else "Erro",
            f"{_tr_multi('Erro') if _tr_multi('Erro') != 'Erro' else 'Erro'}: {e}",
        )
