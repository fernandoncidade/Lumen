from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QCoreApplication
import json
import os
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao

logger = LogManager.get_logger()

def salvar_mapa(self):
    try:
        arquivo, _ = QFileDialog.getSaveFileName(
            self, 
            QCoreApplication.translate("App", "Salvar Mapa Mental"), 
            os.path.join(self.caminho_persistente, "mapa_mental.json"), 
            QCoreApplication.translate("App", "JSON Files (*.json)")
        )

        if arquivo:
            dados = {
                'nos': [
                    {
                        'texto': no.texto,
                        'x': no.scenePos().x(),
                        'y': no.scenePos().y(),
                        'cor': no.cor.name(),
                        'notas': no.notas
                    }
                    for no in self.nos
                ],
                'conexoes': [
                    {
                        'inicio': self.nos.index(linha.no_inicio),
                        'fim': self.nos.index(linha.no_fim)
                    }
                    for linha in self.scene.items() if isinstance(linha, LinhaConexao)
                ]
            }

            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao salvar mapa mental: {str(e)}", exc_info=True)
