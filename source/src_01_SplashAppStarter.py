from typing import Optional
import sys
import multiprocessing
import builtins
from source.utils.LogManager import LogManager


class SplashAppStarter:
    def __init__(self):
        self.logger = LogManager.get_logger()
        self.app = None
        self.splash = None
        self.progress = None
        self.log_widget = None
        self.window = None
        self.translation_manager = None

    def _create_app(self):
        from PySide6.QtWidgets import QApplication
        self.app = QApplication(sys.argv)

        try:
            from source.language.tr_01_gerenciadorTraducao import GerenciadorTraducao
            self.translation_manager = GerenciadorTraducao()

            try:
                self.app.gerenciador_traducao = self.translation_manager

            except Exception:
                try:
                    self.app.setProperty("gerenciador_traducao", self.translation_manager)

                except Exception:
                    pass

            try:
                aplicado = self.translation_manager.aplicar_traducao()
                self.logger.debug(f"Traduções aplicadas na inicialização: {aplicado}")
                try:
                    idioma = self.translation_manager.obter_idioma_atual()
                    self.logger.info(f"Idioma atual do GerenciadorTraducao: {idioma}")
                    import os
                    dir_trad = os.path.join(os.path.dirname(os.path.dirname(__file__)), "language", "translations")
                    if os.path.isdir(dir_trad):
                        files = os.listdir(dir_trad)
                        self.logger.debug(f"Arquivos de tradução disponíveis: {files}")

                except Exception:
                    pass

            except Exception as e:
                self.logger.warning(f"Falha ao aplicar traduções: {e}", exc_info=True)

        except Exception as e:
            self.logger.debug(f"GerenciadorTraducao não inicializado: {e}")

        return self.app

    def _create_splash(self):
        from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar, QTextEdit
        from PySide6.QtGui import QPixmap, QPalette
        from PySide6.QtCore import Qt

        try:
            from source.utils.IconUtils import get_icon_path

        except Exception:
            get_icon_path = None

        try:
            pix = None
            if get_icon_path:
                icon_path = get_icon_path("autismo.ico")
                if icon_path:
                    pix = QPixmap(icon_path)

            if not pix or pix.isNull():
                pix = QPixmap(600, 300)
                pix.fill(Qt.white)

        except Exception:
            pix = QPixmap(600, 300)
            pix.fill(Qt.white)

        orig_pw = pix.width() or 600
        orig_ph = pix.height() or 300
        target_w = max(500, orig_pw * 2)
        target_h = max(300, orig_ph * 2)

        scaled_pix = pix.scaled(target_w, target_h - 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        splash = QWidget()
        splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        splash.setAttribute(Qt.WA_TranslucentBackground, True)
        splash.resize(scaled_pix.width() + 40, scaled_pix.height() + 160)

        layout = QVBoxLayout(splash)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        img_label = QLabel(splash)
        img_label.setPixmap(scaled_pix)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setAttribute(Qt.WA_TranslucentBackground, True)
        layout.addWidget(img_label)

        progress = QProgressBar(splash)
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setTextVisible(True)
        progress.setFixedHeight(18)
        progress.setMinimumWidth(max(200, splash.width() - 40))
        progress.setAttribute(Qt.WA_TranslucentBackground, True)
        progress.setAutoFillBackground(False)
        pal = progress.palette()
        pal.setColor(QPalette.Base, Qt.transparent)
        pal.setColor(QPalette.Window, Qt.transparent)
        progress.setPalette(pal)
        layout.addWidget(progress)

        log_widget = QTextEdit(splash)
        log_widget.setReadOnly(True)
        log_widget.setFixedHeight(80)
        log_widget.setAttribute(Qt.WA_TranslucentBackground, True)
        log_widget.setAutoFillBackground(False)
        pal2 = log_widget.palette()
        pal2.setColor(QPalette.Base, Qt.transparent)
        pal2.setColor(QPalette.Window, Qt.transparent)
        log_widget.setPalette(pal2)
        layout.addWidget(log_widget)

        self.splash = splash
        self.progress = progress
        self.log_widget = log_widget

        if self.app:
            self.app.processEvents()

        return splash

    def _report_progress(self, percent: int, message: Optional[str] = None):
        try:
            if self.progress:
                self.progress.setValue(int(percent))

            if message and self.log_widget:
                self.log_widget.append(message)
                self.log_widget.moveCursor(self.log_widget.textCursor().End)

            if self.app:
                self.app.processEvents()

        except Exception:
            pass

    def _loader(self):
        try:
            from PySide6.QtCore import QCoreApplication

            self._report_progress(5, QCoreApplication.translate("App", "Iniciando carregamento..."))

            seen_modules = set(sys.modules.keys())
            orig_import = builtins.__import__

            def hooked_import(name, globals=None, locals=None, fromlist=(), level=0):
                mod = orig_import(name, globals, locals, fromlist, level)
                try:
                    new = sorted(set(sys.modules.keys()) - seen_modules)
                    for m in new:
                        if m not in seen_modules:
                            seen_modules.add(m)
                            cur = self.progress.value() if self.progress else 0
                            nxt = min(90, cur + 1)
                            prefix = QCoreApplication.translate("App", "Importado:")
                            self._report_progress(nxt, f"{prefix} {m}")

                except Exception:
                    pass

                return mod

            builtins.__import__ = hooked_import

            try:
                from source.src_02_InicializadorMain import montar_e_mostrar_janela, configurar_windows_app_id

                self._report_progress(30, QCoreApplication.translate("App", "Configurando AppUserModelID..."))

                try:
                    configurar_windows_app_id()
                    self._report_progress(40, QCoreApplication.translate("App", "AppUserModelID configurado"))

                except Exception as e:
                    self._report_progress(40, QCoreApplication.translate("App", "Falha AppUserModelID: ") + str(e))

                self.window = montar_e_mostrar_janela(self.app)

            finally:
                builtins.__import__ = orig_import

            self._report_progress(95, QCoreApplication.translate("App", "Finalizando inicialização..."))

            try:
                if self.splash:
                    self.splash.close()

                try:
                    if self.window:
                        self.window.raise_()
                        self.window.activateWindow()

                except Exception:
                    pass

            except Exception:
                if self.splash:
                    self.splash.close()

        except Exception as e:
            self.logger.critical(f"Erro ao carregar aplicação: {e}", exc_info=True)
            try:
                if self.splash:
                    self.splash.close()

            except Exception:
                pass

    def start(self):
        multiprocessing.freeze_support()
        self._create_app()
        self._create_splash()
        self.splash.show()
        if self.app:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self._loader)
            exit_code = self.app.exec()
            sys.exit(exit_code)
