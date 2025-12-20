from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def atualizar_traducoes(self):
    try:
        self.btn_adicionar.setText(QCoreApplication.translate("App", "➕ Adicionar Conceito"))
        self.btn_conectar.setText(QCoreApplication.translate("App", "🔗 Conectar Conceitos"))
        self.btn_cor.setText(QCoreApplication.translate("App", "🎨 Cor"))
        self.btn_salvar.setText(QCoreApplication.translate("App", "💾 Salvar"))
        self.btn_carregar.setText(QCoreApplication.translate("App", "📂 Carregar"))
        self.btn_exportar.setText(QCoreApplication.translate("App", "📸 Exportar PNG"))
        self.btn_limpar.setText(QCoreApplication.translate("App", "🗑️ Limpar"))
        self.btn_importar_doc.setText(QCoreApplication.translate("App", "📄 Importar Documento (IA)"))
        self.btn_reorganizar.setText(QCoreApplication.translate("App", "🤖 Reorganizar com IA"))

        self.label_instrucoes.setText(
            QCoreApplication.translate("App",
                "💡 Duplo-clique nos conceitos para editar | "
                "Arraste para mover | "
                "Use 'Conectar' para criar relações"
            )
        )

        if self.modo_conexao:
            self.btn_conectar.setText(QCoreApplication.translate("App", "🔗 Conectar (Ativo)"))

        if hasattr(self, "_atualizar_traducoes_hierarquia"):
            self._atualizar_traducoes_hierarquia()

    except Exception as e:
        logger.error(f"Erro ao atualizar traduções do MapaMental: {str(e)}", exc_info=True)
