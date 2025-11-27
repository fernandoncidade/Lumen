from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox
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
            f"<p><b>{version_label}</b> 2025.11.26.0</p>"
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
