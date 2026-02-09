from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def atualizar_traducoes(self):
    try:
        self.label_instrucoes.setText(
            QCoreApplication.translate("App",
                "🎓 <b>Método Feynman</b><br>"
                "Aprenda ensinando! Explique conceitos complexos com suas próprias palavras, como se estivesse ensinando para alguém que nunca viu o assunto."
            )
        )

        self.label_meus_conceitos.setText(QCoreApplication.translate("App", "📚 Meus Conceitos:"))

        self.btn_novo.setText(QCoreApplication.translate("App", "➕ Novo"))
        self.btn_deletar.setText(QCoreApplication.translate("App", "🗑️ Deletar"))

        self.label_conceito.setText(QCoreApplication.translate("App", "Conceito:"))

        self.input_titulo.setPlaceholderText(QCoreApplication.translate("App", "Ex: Tensão de Cisalhamento"))

        self.label_passo1.setText(QCoreApplication.translate("App", "1️⃣ <b>Explique com Simplicidade</b> (como para uma criança):"))

        self.texto_explicacao.setPlaceholderText(QCoreApplication.translate("App", "Escreva sua explicação usando linguagem simples e exemplos do dia-a-dia."))

        self.label_passo2.setText(QCoreApplication.translate("App", "2️⃣ <b>Lacunas Identificadas</b> (o que você não conseguiu explicar bem?):"))

        self.texto_lacunas.setPlaceholderText(QCoreApplication.translate("App", "Liste os pontos onde você travou ou ficou confuso."))

        self.label_passo3.setText(QCoreApplication.translate("App","3️⃣ <b>Revisão e Simplificação Final</b> (depois de estudar as lacunas):"))

        self.texto_revisao.setPlaceholderText(QCoreApplication.translate("App", "Reescreva sua explicação de forma ainda mais clara e completa."))

        self.label_nivel.setText(QCoreApplication.translate("App", "📊 Nível de Domínio:"))

        indice_atual = self.combo_dominio.currentIndex()
        self.combo_dominio.clear()
        self.combo_dominio.addItems([
            QCoreApplication.translate("App", "🔴 Iniciante (não consigo explicar)"),
            QCoreApplication.translate("App", "🟡 Intermediário (explico com dificuldade)"),
            QCoreApplication.translate("App", "🟢 Avançado (explico facilmente)")
        ])
        if indice_atual >= 0:
            self.combo_dominio.setCurrentIndex(indice_atual)

        self.gerenciador_botoes.set_button_text(self.btn_salvar, QCoreApplication.translate("App", "💾 Salvar Conceito"))

    except Exception as e:
        logger.error(f"Erro ao atualizar traduções do MetodoFeynman: {str(e)}", exc_info=True)
