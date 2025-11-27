from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def show_help(self):
    try:
        help_text = QCoreApplication.translate("App", """
        <h2>Estudo Acessível - Atalhos</h2>
        <table>
            <tr><td><b>Ctrl+1</b></td><td>Leitor Acessível</td></tr>
            <tr><td><b>Ctrl+2</b></td><td>Gestão de Tempo</td></tr>
            <tr><td><b>Ctrl+3</b></td><td>Mapas Mentais</td></tr>
            <tr><td><b>Ctrl+4</b></td><td>Método Feynman</td></tr>
            <tr><td><b>Ctrl+Q</b></td><td>Sair da aplicação</td></tr>
            <tr><td><b>F1</b></td><td>Ajuda</td></tr>
        </table>
        <br>
        <p><b>Régua de Foco:</b></p>
        <ul>
            <li>Arraste no centro para mover</li>
            <li>Arraste nas bordas para redimensionar</li>
            <li>Setas ↑↓←→ para ajuste fino</li>
            <li>ESC para fechar</li>
        </ul>
        """)
        QMessageBox.information(self, QCoreApplication.translate("App", "Ajuda - Atalhos"), help_text)

    except Exception as e:
        logger.critical(f"Erro crítico ao exibir ajuda: {str(e)}", exc_info=True)
