from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def atualizar_menu(self):
    try:
        if not hasattr(self, 'menu_arquivo'):
            return

        self.menu_arquivo.setTitle(QCoreApplication.translate("App", "📁 Arquivo"))

        if hasattr(self, 'action_atalhos'):
            self.action_atalhos.setText(QCoreApplication.translate("App", "📚 Ajuda - Atalhos"))
            try:
                from PySide6.QtCore import Qt
                self.action_atalhos.setShortcut("F1")
                self.action_atalhos.setShortcutContext(Qt.ApplicationShortcut)

            except Exception:
                pass

        self.submenu_leitor.setTitle(QCoreApplication.translate("App", "📖 Leitor Acessível"))
        self.action_carregar_pdf.setText(QCoreApplication.translate("App", "📁 Carregar PDF"))
        self.action_ler_texto.setText(QCoreApplication.translate("App", "▶️ Ler"))
        self.action_pausar_leitura.setText(QCoreApplication.translate("App", "⏸️ Pausar"))

        if hasattr(self, 'action_parar_leitura'):
            self.action_parar_leitura.setText(QCoreApplication.translate("App", "⏹️ Parar"))

        self.action_regua_foco.setText(QCoreApplication.translate("App", "📏 Ativar Régua de Foco"))

        self.submenu_tempo.setTitle(QCoreApplication.translate("App", "⏱️ Gestão de Tempo"))
        self.action_adicionar_tarefa.setText(QCoreApplication.translate("App", "➕ Adicionar"))
        self.action_iniciar_pomodoro.setText(QCoreApplication.translate("App", "▶️ Iniciar"))
        self.action_resetar_pomodoro.setText(QCoreApplication.translate("App", "⏱️ Resetar Relógio"))

        if hasattr(self, 'action_resetar_ciclo'):
            self.action_resetar_ciclo.setText(QCoreApplication.translate("App", "🔄 Resetar Ciclo"))

        if hasattr(self, 'action_pular_ciclo'):
            self.action_pular_ciclo.setText(QCoreApplication.translate("App", "⏭️ Pular"))

        self.submenu_mapa.setTitle(QCoreApplication.translate("App", "🧠 Mapas Mentais"))
        self.action_adicionar_conceito.setText(QCoreApplication.translate("App", "➕ Adicionar Conceito"))
        self.action_conectar_conceitos.setText(QCoreApplication.translate("App", "🔗 Conectar Conceitos"))
        self.action_salvar_mapa.setText(QCoreApplication.translate("App", "💾 Salvar"))
        self.action_carregar_mapa.setText(QCoreApplication.translate("App", "📂 Carregar"))
        self.action_exportar_mapa.setText(QCoreApplication.translate("App", "📸 Exportar PNG"))
        self.action_limpar_mapa.setText(QCoreApplication.translate("App", "🗑️ Limpar"))

        self.submenu_feynman.setTitle(QCoreApplication.translate("App", "🎓 Método Feynman"))
        self.action_novo_conceito.setText(QCoreApplication.translate("App", "➕ Novo"))
        self.action_salvar_conceito.setText(QCoreApplication.translate("App", "💾 Salvar Conceito"))
        self.action_deletar_conceito.setText(QCoreApplication.translate("App", "🗑️ Deletar"))

        self.submenu_eisenhower.setTitle(QCoreApplication.translate("App", "🗂️ Matriz Eisenhower"))
        self.action_eis_novo.setText(QCoreApplication.translate("App", "🆕 Novo"))
        self.action_eis_abrir.setText(QCoreApplication.translate("App", "📂 Abrir"))
        self.action_eis_salvar.setText(QCoreApplication.translate("App", "💾 Salvar"))
        self.action_eis_limpar.setText(QCoreApplication.translate("App", "🗑️ Limpar"))

        if self.action_eis_calendario.isChecked():
            self.action_eis_calendario.setText(QCoreApplication.translate("App","📅 Ocultar Calendário"))

        else:
            self.action_eis_calendario.setText(QCoreApplication.translate("App","📅 Mostrar Calendário"))

        self.action_sair.setText(QCoreApplication.translate("App", "🚪 Sair"))

        self.menu_config.setTitle(QCoreApplication.translate("App", "⚙️ Configurações"))
        self.menu_idiomas.setTitle(QCoreApplication.translate("App", "🌐 Idiomas"))
        self.menu_vozes.setTitle(QCoreApplication.translate("App", "🗣️ Vozes"))

        if hasattr(self, 'action_config_font'):
            self.action_config_font.setText(QCoreApplication.translate("App", "🔤 Fonte..."))

        if hasattr(self, 'action_config_sound'):
            self.action_config_sound.setText(QCoreApplication.translate("App", "🔔 Som..."))

        self.action_pt_br.setText(QCoreApplication.translate("App", "🇧🇷 Português (Brasil)"))
        self.action_en_us.setText(QCoreApplication.translate("App", "🇺🇸 English (United States)"))

    except Exception as e:
        logger.error(f"Erro ao atualizar menu: {str(e)}", exc_info=True)
