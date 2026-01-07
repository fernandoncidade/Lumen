from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def show_help(self):
    try:
        title = QCoreApplication.translate("App", "Lúmen - Atalhos")

        atalhos = [
            (QCoreApplication.translate("App", "Ctrl+1"), QCoreApplication.translate("App", "📖 Leitor Acessível")),
            (QCoreApplication.translate("App", "Ctrl+2"), QCoreApplication.translate("App", "⏱️ Gestão de Tempo")),
            (QCoreApplication.translate("App", "Ctrl+3"), QCoreApplication.translate("App", "🧠 Mapas Mentais")),
            (QCoreApplication.translate("App", "Ctrl+4"), QCoreApplication.translate("App", "🎓 Método Feynman")),
            (QCoreApplication.translate("App", "Ctrl+5"), QCoreApplication.translate("App", "🗂️ Matriz Eisenhower")),
            (QCoreApplication.translate("App", "Ctrl+O"), QCoreApplication.translate("App", "📁 Carregar PDF")),
            (QCoreApplication.translate("App", "Ctrl+R"), QCoreApplication.translate("App", "▶️ Ler")),
            (QCoreApplication.translate("App", "Ctrl+P"), QCoreApplication.translate("App", "⏸️ Pausar")),
            (QCoreApplication.translate("App", "Ctrl+T"), QCoreApplication.translate("App", "➕ Adicionar")),
            (QCoreApplication.translate("App", "Ctrl+N"), QCoreApplication.translate("App", "➕ Adicionar Conceito")),
            (QCoreApplication.translate("App", "Ctrl+S"), QCoreApplication.translate("App", "💾 Salvar")),
            (QCoreApplication.translate("App", "Ctrl+L"), QCoreApplication.translate("App", "📂 Carregar")),
            (QCoreApplication.translate("App", "Ctrl+F"), QCoreApplication.translate("App", "🔎 Buscar")),
            (QCoreApplication.translate("App", "Ctrl+Shift+F"), QCoreApplication.translate("App", "🔤 Fonte...")),
            (QCoreApplication.translate("App", "Ctrl+Shift+S"), QCoreApplication.translate("App", "🔔 Som...")),
            (QCoreApplication.translate("App", "Ctrl+Q"), QCoreApplication.translate("App", "🚪 Sair")),
            (QCoreApplication.translate("App", "F1"), QCoreApplication.translate("App", "Ajuda")),
        ]

        regua_title = QCoreApplication.translate("App", "Régua de Foco:")
        regua_items = [
            QCoreApplication.translate("App", "Arraste no centro para mover"),
            QCoreApplication.translate("App", "Arraste nas bordas para redimensionar"),
            QCoreApplication.translate("App", "Setas ↑↓←→ para ajuste fino"),
            QCoreApplication.translate("App", "ESC para fechar"),
        ]

        rows_html = "".join(f"<tr><td><b>{k}</b></td><td>{v}</td></tr>" for k, v in atalhos)
        regua_html = "".join(f"<li>{it}</li>" for it in regua_items)

        help_html = (
            f"<h2>{title}</h2>"
            f"<table>{rows_html}</table>"
            f"<br><p><b>{regua_title}</b></p>"
            f"<ul>{regua_html}</ul>"
        )

        QMessageBox.information(self, QCoreApplication.translate("App", "Ajuda - Atalhos"), help_html)

    except Exception as e:
        logger.critical(f"Erro crítico ao exibir ajuda: {str(e)}", exc_info=True)
