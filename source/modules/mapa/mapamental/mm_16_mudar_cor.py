from PySide6.QtWidgets import QColorDialog
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QBrush
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_01_NoConceito import NoConceito

logger = LogManager.get_logger()

def mudar_cor(self):
    try:
        selecionados = [item for item in self.scene.selectedItems() if isinstance(item, NoConceito)]

        if not selecionados:
            return

        from PySide6.QtWidgets import QLabel, QPushButton, QGroupBox

        dialogo = QColorDialog(self)
        dialogo.setOption(QColorDialog.DontUseNativeDialog, True)
        dialogo.setOption(QColorDialog.ShowAlphaChannel, False)
        dialogo.setWindowTitle(QCoreApplication.translate("App", "advanced_color_picker"))
        dialogo.setModal(True)

        mapa_textos = {
            "Basic colors": "basic_colors",
            "&Basic colors": "basic_colors",
            "Custom colors": "custom_colors",
            "&Custom colors": "custom_colors",
            "Pick Screen Color": "pick_screen_color",
            "&Pick Screen Color": "pick_screen_color",
            "Add to Custom Colors": "add_to_custom_colors",
            "&Add to Custom Colors": "add_to_custom_colors",
            "Hue:": "hue",
            "&Hue:": "hue",
            "Sat:": "sat",
            "&Sat:": "sat",
            "Val:": "val",
            "&Val:": "val",
            "Red:": "red",
            "&Red:": "red",
            "Green:": "green",
            "&Green:": "green",
            "Blue:": "blue",
            "&Blue:": "blue",
            "HTML:": "html",
            "&HTML:": "html",
            "OK": "ok",
            "&OK": "ok",
            "Cancel": "cancel",
            "&Cancel": "cancel"
        }

        def normalizar(texto: str) -> str:
            return texto.strip().replace(":", "").replace("&", "")

        try:
            for label in dialogo.findChildren(QLabel):
                txt = label.text().strip()
                if not txt:
                    continue

                txt_norm = normalizar(txt)
                for chave_orig, chave_trad in mapa_textos.items():
                    if normalizar(chave_orig) == txt_norm:
                        traducao = QCoreApplication.translate("App", chave_trad)
                        label.setText(f"{traducao}:" if ":" in txt else traducao)
                        break

        except Exception:
            pass

        try:
            for btn in dialogo.findChildren(QPushButton):
                txt = btn.text().strip()
                if not txt:
                    continue

                txt_norm = normalizar(txt)
                for chave_orig, chave_trad in mapa_textos.items():
                    if normalizar(chave_orig) == txt_norm:
                        btn.setText(QCoreApplication.translate("App", chave_trad))
                        break

        except Exception:
            pass

        try:
            for gb in dialogo.findChildren(QGroupBox):
                txt = gb.title().strip()
                if not txt:
                    continue

                txt_norm = normalizar(txt)
                for chave_orig, chave_trad in mapa_textos.items():
                    if normalizar(chave_orig) == txt_norm:
                        gb.setTitle(QCoreApplication.translate("App", chave_trad))
                        break

        except Exception:
            pass

        if dialogo.exec():
            cor = dialogo.selectedColor()
            if cor.isValid():
                for no in selecionados:
                    no.cor = cor
                    no.setBrush(QBrush(cor))

    except Exception as e:
        logger.error(f"Erro ao mudar cor: {str(e)}", exc_info=True)
