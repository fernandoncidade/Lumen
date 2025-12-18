from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QColor
import json
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_01_NoConceito import NoConceito
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao

logger = LogManager.get_logger()

def carregar_mapa(self):
    try:
        arquivo, _ = QFileDialog.getOpenFileName(
            self, 
            QCoreApplication.translate("App", "Carregar Mapa Mental"), 
            self.caminho_persistente, 
            QCoreApplication.translate("App", "JSON Files (*.json)")
        )

        if arquivo:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)

            self.limpar_mapa()

            for no_data in dados['nos']:
                no = NoConceito(no_data['x'], no_data['y'], no_data['texto'], QColor(no_data['cor']))
                no.notas = no_data.get('notas', '')
                self.scene.addItem(no)
                self.nos.append(no)

            for con_data in dados['conexoes']:
                linha = LinhaConexao(self.nos[con_data['inicio']], self.nos[con_data['fim']])
                self.scene.addItem(linha)

    except Exception as e:
        logger.error(f"Erro ao carregar mapa mental: {str(e)}", exc_info=True)
