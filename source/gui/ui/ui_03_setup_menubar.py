from PySide6.QtWidgets import QDialog
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication, Qt
from source.utils.LogManager import LogManager
from source.gui.ui.ui_22_font_config_dialog import FontConfigDialog
from source.gui.ui.ui_23_sound_config_dialog import SoundConfigDialog
logger = LogManager.get_logger()

def setup_menubar(self):
    try:
        self.menubar = self.menuBar()

        self.menu_arquivo = self.menubar.addMenu(QCoreApplication.translate("App", "📁 Arquivo"))

        self.submenu_leitor = self.menu_arquivo.addMenu(QCoreApplication.translate("App", "📖 Leitor Acessível"))

        self.action_carregar_pdf = QAction(QCoreApplication.translate("App", "📁 Carregar PDF"), self)
        self.action_carregar_pdf.setShortcut("Ctrl+O")
        self.action_carregar_pdf.triggered.connect(lambda: self.executar_acao_modulo('leitor', 'carregar_pdf'))
        self.submenu_leitor.addAction(self.action_carregar_pdf)

        self.action_ler_texto = QAction(QCoreApplication.translate("App", "▶️ Ler"), self)
        self.action_ler_texto.setShortcut("Ctrl+R")
        self.action_ler_texto.triggered.connect(lambda: self.executar_acao_modulo('leitor', 'iniciar_leitura'))
        self.submenu_leitor.addAction(self.action_ler_texto)

        self.action_pausar_leitura = QAction(QCoreApplication.translate("App", "⏸️ Pausar"), self)
        self.action_pausar_leitura.setShortcut("Ctrl+P")
        self.action_pausar_leitura.triggered.connect(lambda: self.executar_acao_modulo('leitor', 'pausar_leitura'))
        self.submenu_leitor.addAction(self.action_pausar_leitura)

        self.action_parar_leitura = QAction(QCoreApplication.translate("App", "⏹️ Parar"), self)
        self.action_parar_leitura.triggered.connect(lambda: self.executar_acao_modulo('leitor', 'parar_leitura'))
        self.submenu_leitor.addAction(self.action_parar_leitura)

        self.submenu_leitor.addSeparator()

        self.action_regua_foco = QAction(QCoreApplication.translate("App", "📏 Ativar Régua de Foco"), self)
        self.action_regua_foco.setCheckable(True)
        self.action_regua_foco.triggered.connect(lambda: self.executar_acao_modulo('leitor', 'toggle_regua_foco'))
        self.submenu_leitor.addAction(self.action_regua_foco)

        self.submenu_tempo = self.menu_arquivo.addMenu(QCoreApplication.translate("App", "⏱️ Gestão de Tempo"))

        self.action_adicionar_tarefa = QAction(QCoreApplication.translate("App", "➕ Adicionar"), self)
        self.action_adicionar_tarefa.setShortcut("Ctrl+T")

        try:
            self.action_adicionar_tarefa.setShortcutContext(Qt.ApplicationShortcut)

        except Exception:
            pass

        try:
            if hasattr(self, 'addAction'):
                self.addAction(self.action_adicionar_tarefa)

        except Exception:
            pass

        def _on_add_task():
            try:
                logger.info("menu: _on_add_task acionado via atalho/menu")
                try:
                    if hasattr(self, 'switch_to_tab'):
                        self.switch_to_tab(1)

                except Exception:
                    pass

                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self.executar_acao_modulo('gerenciador', 'adicionar_tarefa'))

            except Exception as e:
                logger.error(f"Erro ao processar adicionar tarefa via atalho: {e}", exc_info=True)

        self.action_adicionar_tarefa.triggered.connect(_on_add_task)
        self.submenu_tempo.addAction(self.action_adicionar_tarefa)

        self.submenu_tempo.addSeparator()

        self.action_iniciar_pomodoro = QAction(QCoreApplication.translate("App", "▶️ Iniciar"), self)
        self.action_iniciar_pomodoro.triggered.connect(lambda: self.executar_acao_modulo('gerenciador', 'toggle_timer'))
        self.submenu_tempo.addAction(self.action_iniciar_pomodoro)

        self.action_resetar_pomodoro = QAction(QCoreApplication.translate("App", "⏱️ Resetar Relógio"), self)
        self.action_resetar_pomodoro.triggered.connect(lambda: self.executar_acao_modulo('gerenciador', 'resetar_timer'))
        self.submenu_tempo.addAction(self.action_resetar_pomodoro)

        self.action_resetar_ciclo = QAction(QCoreApplication.translate("App", "🔄 Resetar Ciclo"), self)
        self.action_resetar_ciclo.triggered.connect(lambda: self.executar_acao_modulo('gerenciador', 'resetar_ciclo'))
        self.submenu_tempo.addAction(self.action_resetar_ciclo)

        self.action_pular_ciclo = QAction(QCoreApplication.translate("App", "⏭️ Pular"), self)
        self.action_pular_ciclo.triggered.connect(lambda: self.executar_acao_modulo('gerenciador', 'pular_ciclo'))
        self.submenu_tempo.addAction(self.action_pular_ciclo)

        self.submenu_mapa = self.menu_arquivo.addMenu(QCoreApplication.translate("App", "🧠 Mapas Mentais"))

        self.action_adicionar_conceito = QAction(QCoreApplication.translate("App", "➕ Adicionar Conceito"), self)
        self.action_adicionar_conceito.setShortcut("Ctrl+N")
        self.action_adicionar_conceito.triggered.connect(lambda: self.executar_acao_modulo('mapa', 'adicionar_no'))
        self.submenu_mapa.addAction(self.action_adicionar_conceito)

        self.action_conectar_conceitos = QAction(QCoreApplication.translate("App", "🔗 Conectar Conceitos"), self)
        self.action_conectar_conceitos.setCheckable(True)
        self.action_conectar_conceitos.triggered.connect(lambda: self.executar_acao_modulo('mapa', 'toggle_modo_conexao'))
        self.submenu_mapa.addAction(self.action_conectar_conceitos)

        self.submenu_mapa.addSeparator()

        self.action_salvar_mapa = QAction(QCoreApplication.translate("App", "💾 Salvar"), self)
        self.action_salvar_mapa.setShortcut("Ctrl+S")
        self.action_salvar_mapa.triggered.connect(lambda: self.executar_acao_modulo('mapa', 'salvar_mapa'))
        self.submenu_mapa.addAction(self.action_salvar_mapa)

        self.action_carregar_mapa = QAction(QCoreApplication.translate("App", "📂 Carregar"), self)
        self.action_carregar_mapa.setShortcut("Ctrl+L")
        self.action_carregar_mapa.triggered.connect(lambda: self.executar_acao_modulo('mapa', 'carregar_mapa'))
        self.submenu_mapa.addAction(self.action_carregar_mapa)

        self.action_exportar_mapa = QAction(QCoreApplication.translate("App", "📸 Exportar PNG"), self)
        self.action_exportar_mapa.triggered.connect(lambda: self.executar_acao_modulo('mapa', 'exportar_imagem'))
        self.submenu_mapa.addAction(self.action_exportar_mapa)

        self.action_limpar_mapa = QAction(QCoreApplication.translate("App", "🗑️ Limpar"), self)
        self.action_limpar_mapa.triggered.connect(lambda: self.executar_acao_modulo('mapa', 'limpar_mapa'))
        self.submenu_mapa.addAction(self.action_limpar_mapa)

        self.submenu_feynman = self.menu_arquivo.addMenu(QCoreApplication.translate("App", "🎓 Método Feynman"))

        self.action_novo_conceito = QAction(QCoreApplication.translate("App", "➕ Novo"), self)
        self.action_novo_conceito.triggered.connect(lambda: self.executar_acao_modulo('feynman', 'novo_conceito'))
        self.submenu_feynman.addAction(self.action_novo_conceito)

        self.action_salvar_conceito = QAction(QCoreApplication.translate("App", "💾 Salvar Conceito"), self)
        self.action_salvar_conceito.triggered.connect(lambda: self.executar_acao_modulo('feynman', 'salvar_conceito_atual'))
        self.submenu_feynman.addAction(self.action_salvar_conceito)

        self.action_deletar_conceito = QAction(QCoreApplication.translate("App", "🗑️ Deletar"), self)
        self.action_deletar_conceito.triggered.connect(lambda: self.executar_acao_modulo('feynman', 'deletar_conceito'))
        self.submenu_feynman.addAction(self.action_deletar_conceito)

        self.submenu_eisenhower = self.menu_arquivo.addMenu(QCoreApplication.translate("App", "🗂️ Matriz Eisenhower"))

        self.action_eis_novo = QAction(QCoreApplication.translate("App", "🆕 Novo"), self)
        self.action_eis_novo.triggered.connect(lambda: self.executar_acao_modulo('eisenhower', 'novo'))
        self.submenu_eisenhower.addAction(self.action_eis_novo)

        self.action_eis_abrir = QAction(QCoreApplication.translate("App", "📂 Abrir"), self)
        self.action_eis_abrir.triggered.connect(lambda: self.executar_acao_modulo('eisenhower', 'abrir'))
        self.submenu_eisenhower.addAction(self.action_eis_abrir)

        self.action_eis_salvar = QAction(QCoreApplication.translate("App", "💾 Salvar"), self)
        self.action_eis_salvar.triggered.connect(lambda: self.executar_acao_modulo('eisenhower', 'salvar'))
        self.submenu_eisenhower.addAction(self.action_eis_salvar)

        self.action_eis_limpar = QAction(QCoreApplication.translate("App", "🗑️ Limpar"), self)
        self.action_eis_limpar.triggered.connect(lambda: self.executar_acao_modulo('eisenhower', 'limpar'))
        self.submenu_eisenhower.addAction(self.action_eis_limpar)

        self.submenu_eisenhower.addSeparator()

        self.action_eis_calendario = QAction(QCoreApplication.translate("App", "📅 Mostrar Calendário"), self)
        self.action_eis_calendario.setCheckable(True)
        self.action_eis_calendario.triggered.connect(lambda: self.executar_acao_modulo('eisenhower', 'calendar_toggle'))
        self.submenu_eisenhower.addAction(self.action_eis_calendario)

        self.action_atalhos = QAction(QCoreApplication.translate("App", "📚 Ajuda - Atalhos"), self)
        self.action_atalhos.setShortcut("F1")
        self.action_atalhos.triggered.connect(self.show_help)

        try:
            self.action_atalhos.setShortcutContext(Qt.ApplicationShortcut)

        except Exception:
            pass

        self.menu_arquivo.addAction(self.action_atalhos)

        self.menu_arquivo.addSeparator()

        self.action_sair = QAction(QCoreApplication.translate("App", "🚪 Sair"), self)
        self.action_sair.setShortcut("Ctrl+Q")

        try:
            self.action_sair.setShortcutContext(Qt.ApplicationShortcut)

        except Exception:
            pass

        try:
            if hasattr(self, 'addAction'):
                self.addAction(self.action_sair)

        except Exception:
            pass

        self.action_sair.triggered.connect(self.close)
        self.menu_arquivo.addAction(self.action_sair)

        self.menu_config = self.menubar.addMenu(QCoreApplication.translate("App", "⚙️ Configurações"))

        self.menu_idiomas = self.menu_config.addMenu(QCoreApplication.translate("App", "🌐 Idiomas"))

        self.action_pt_br = QAction(QCoreApplication.translate("App", "🇧🇷 Português (Brasil)"), self)
        self.action_pt_br.setCheckable(True)
        self.action_pt_br.triggered.connect(lambda: self.mudar_idioma("pt_BR"))
        self.menu_idiomas.addAction(self.action_pt_br)

        self.action_en_us = QAction(QCoreApplication.translate("App", "🇺🇸 English (United States)"), self)
        self.action_en_us.setCheckable(True)
        self.action_en_us.triggered.connect(lambda: self.mudar_idioma("en_US"))
        self.menu_idiomas.addAction(self.action_en_us)

        idioma_atual = self.tradutor.obter_idioma_atual()
        if idioma_atual == "pt_BR":
            self.action_pt_br.setChecked(True)

        else:
            self.action_en_us.setChecked(True)

        self.action_config_font = QAction(QCoreApplication.translate("App", "🔤 Fonte..."), self)
        self.action_config_font.setShortcut("Ctrl+Shift+F")
        def _open_font_dialog():
            try:
                dlg = FontConfigDialog(self)
                result = dlg.exec()
                if result == QDialog.Accepted:
                    try:
                        if hasattr(self, 'atualizar_modulos'):
                            self.atualizar_modulos()

                        else:
                            logger.info("atualizar_modulos não encontrada; fontes aplicadas via diálogo")

                    except Exception as e:
                        logger.error(f"Erro ao aplicar fonte nos módulos: {e}", exc_info=True)

            except Exception as e:
                logger.error(f"Erro ao abrir FontConfigDialog: {e}", exc_info=True)

        self.action_config_font.triggered.connect(_open_font_dialog)
        self.menu_config.addAction(self.action_config_font)

        self.action_config_sound = QAction(QCoreApplication.translate("App", "🔔 Som..."), self)
        self.action_config_sound.setShortcut("Ctrl+Shift+S")
        def _open_sound_dialog():
            try:
                dlg = SoundConfigDialog(self)
                result_sound = dlg.exec()
                if result_sound == QDialog.Accepted:
                    try:
                        if hasattr(self, 'atualizar_modulos'):
                            self.atualizar_modulos()

                        else:
                            logger.info("atualizar_modulos não encontrada; configurações de som aplicadas via diálogo")

                    except Exception as e:
                        logger.error(f"Erro ao aplicar configurações de som nos módulos: {e}", exc_info=True)

            except Exception as e:
                logger.error(f"Erro ao abrir SoundConfigDialog: {e}", exc_info=True)

        self.action_config_sound.triggered.connect(_open_sound_dialog)
        self.menu_config.addAction(self.action_config_sound)

        self.menu_vozes = self.menu_config.addMenu(QCoreApplication.translate("App", "🗣️ Vozes"))
        self.actions_vozes = []
        self.carregar_vozes()

        self.menu_sobre = self.menubar.addMenu(QCoreApplication.translate("App", "ℹ️ Sobre"))
        self.action_sobre_app = QAction(QCoreApplication.translate("App", "ℹ️ Sobre o Aplicativo"), self)
        self.action_sobre_app.triggered.connect(self.exibir_sobre)
        self.menu_sobre.addAction(self.action_sobre_app)

        def _open_manual():
            try:
                from source.modules.mod_07_exibir_public import exibir_manual
                exibir_manual(self)

            except Exception as e:
                logger.error(f"Erro ao abrir Manual: {e}", exc_info=True)

        self.action_manual = QAction(QCoreApplication.translate("App", "📃 Manual"), self)
        self.action_manual.triggered.connect(_open_manual)
        self.menu_sobre.addAction(self.action_manual)

        self.menu_sobre.addSeparator()

    except Exception as e:
        logger.error(f"Erro ao configurar barra de menu: {str(e)}", exc_info=True)
