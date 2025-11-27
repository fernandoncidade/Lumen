from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def mudar_idioma(self, codigo_idioma):
    try:
        idioma_anterior = self.tradutor.obter_idioma_atual()

        if codigo_idioma == idioma_anterior:
            return

        if self.tradutor.definir_idioma(codigo_idioma):
            self.action_pt_br.setChecked(codigo_idioma == "pt_BR")
            self.action_en_us.setChecked(codigo_idioma == "en_US")

            self.atualizar_interface(codigo_idioma)
            self.atualizar_modulos()

            QMessageBox.information(
                self,
                QCoreApplication.translate("App", "✅ Idioma Alterado"),
                QCoreApplication.translate("App", "O idioma foi alterado com sucesso!")
            )

        else:
            QMessageBox.warning(
                self,
                QCoreApplication.translate("App", "⚠️ Erro"),
                QCoreApplication.translate("App", "Não foi possível alterar o idioma.")
            )

    except Exception as e:
        logger.error(f"Erro ao mudar idioma: {str(e)}", exc_info=True)
