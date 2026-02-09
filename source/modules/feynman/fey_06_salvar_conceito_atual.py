from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def salvar_conceito_atual(self):
    try:
        titulo = self.input_titulo.toPlainText().strip()

        if not titulo:
            QMessageBox.warning(
                self, 
                QCoreApplication.translate("App", "Atenção"), 
                QCoreApplication.translate("App", "Por favor, digite o título do conceito!")
            )
            return

        conceito = {
            'titulo': titulo,
            'explicacao': self.texto_explicacao.toPlainText(),
            'lacunas': self.texto_lacunas.toPlainText(),
            'revisao': self.texto_revisao.toPlainText(),
            'dominio': self.combo_dominio.currentIndex()
        }

        existente = next((c for c in self.conceitos if c['titulo'] == titulo), None)
        if existente:
            self.conceitos[self.conceitos.index(existente)] = conceito

        else:
            self.conceitos.append(conceito)

        self.salvar_conceitos()
        self.atualizar_lista()

        QMessageBox.information(
            self, 
            QCoreApplication.translate("App", "✅ Salvo"), 
            QCoreApplication.translate("App", "Conceito '{titulo}' salvo com sucesso!").format(titulo=titulo)
        )

    except Exception as e:
        logger.error(f"Erro ao salvar conceito atual: {str(e)}", exc_info=True)
