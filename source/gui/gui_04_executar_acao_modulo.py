from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def executar_acao_modulo(self, modulo, acao):
    try:
        if modulo == 'leitor' and hasattr(self, 'leitor'):
            if acao == 'carregar_pdf':
                self.tabs.setCurrentIndex(0)
                self.leitor.carregar_pdf()

            elif acao == 'iniciar_leitura':
                    self.tabs.setCurrentIndex(0)
                    self.leitor.iniciar_leitura()
                    try:
                        if hasattr(self, 'action_pausar_leitura'):
                            self.action_pausar_leitura.setText(QCoreApplication.translate("App", "⏸️ Pausar"))

                    except Exception:
                        pass

            elif acao == 'pausar_leitura':
                self.tabs.setCurrentIndex(0)
                try:
                    self.leitor.pausar_leitura()
                    try:
                        if hasattr(self, 'action_pausar_leitura') and hasattr(self.leitor, '_is_paused'):
                            if getattr(self.leitor, '_is_paused', False):
                                self.action_pausar_leitura.setText(QCoreApplication.translate("App", "▶️ Continuar"))

                            else:
                                self.action_pausar_leitura.setText(QCoreApplication.translate("App", "⏸️ Pausar"))

                    except Exception:
                        pass

                except Exception as e:
                    logger.error(f"Erro ao executar ação de pausa via menu: {e}", exc_info=True)

            elif acao == 'parar_leitura':
                self.tabs.setCurrentIndex(0)
                try:
                    self.leitor.parar_leitura()
                    try:
                        if hasattr(self, 'action_pausar_leitura'):
                            self.action_pausar_leitura.setText(QCoreApplication.translate("App", "⏸️ Pausar"))

                    except Exception:
                        pass

                except Exception as e:
                    logger.error(f"Erro ao executar parar_leitura via menu: {e}", exc_info=True)

            elif acao == 'toggle_regua_foco':
                self.tabs.setCurrentIndex(0)
                novo_estado = not self.leitor.btn_regua.isChecked()
                self.leitor.btn_regua.setChecked(novo_estado)
                self.leitor.toggle_regua_foco()
                self.action_regua_foco.setChecked(self.leitor.btn_regua.isChecked())

        elif modulo == 'gerenciador' and hasattr(self, 'gerenciador'):
            if acao == 'adicionar_tarefa':
                self.tabs.setCurrentIndex(1)
                self.gerenciador.tarefas.input_tarefa.setFocus()

            elif acao == 'toggle_timer':
                self.tabs.setCurrentIndex(1)
                self.gerenciador.pomodoro.toggle_timer()

            elif acao == 'resetar_timer':
                self.tabs.setCurrentIndex(1)
                self.gerenciador.pomodoro.resetar_timer()

            elif acao == 'resetar_ciclo':
                self.tabs.setCurrentIndex(1)
                self.gerenciador.pomodoro.resetar_ciclo()

            elif acao == 'pular_ciclo':
                self.tabs.setCurrentIndex(1)
                self.gerenciador.pomodoro.pular_ciclo()

        elif modulo == 'mapa' and hasattr(self, 'mapa'):
            if acao == 'adicionar_no':
                self.tabs.setCurrentIndex(2)
                self.mapa.adicionar_no()

            elif acao == 'toggle_modo_conexao':
                self.tabs.setCurrentIndex(2)
                self.mapa.toggle_modo_conexao()
                self.action_conectar_conceitos.setChecked(self.mapa.btn_conectar.isChecked())

            elif acao == 'salvar_mapa':
                self.tabs.setCurrentIndex(2)
                self.mapa.salvar_mapa()

            elif acao == 'carregar_mapa':
                self.tabs.setCurrentIndex(2)
                self.mapa.carregar_mapa()

            elif acao == 'exportar_imagem':
                self.tabs.setCurrentIndex(2)
                self.mapa.exportar_imagem()

            elif acao == 'limpar_mapa':
                self.tabs.setCurrentIndex(2)
                self.mapa.limpar_mapa()

        elif modulo == 'feynman' and hasattr(self, 'feynman'):
            if acao == 'novo_conceito':
                self.tabs.setCurrentIndex(3)
                self.feynman.novo_conceito()

            elif acao == 'salvar_conceito_atual':
                self.tabs.setCurrentIndex(3)
                self.feynman.salvar_conceito_atual()

            elif acao == 'deletar_conceito':
                self.tabs.setCurrentIndex(3)
                self.feynman.deletar_conceito()

        elif modulo == 'eisenhower' and hasattr(self, 'eisenhower'):
            idx = 4

            if acao in ('novo','abrir','salvar','limpar','calendar_toggle'):
                 self.tabs.setCurrentIndex(idx)

            if acao == 'novo':
                self.eisenhower.nova_sessao()

            elif acao == 'abrir':
                self.eisenhower.abrir_arquivo()

            elif acao == 'salvar':
                self.eisenhower.salvar_como()

            elif acao == 'limpar':
                self.eisenhower.limpar_tudo()

            elif acao == 'calendar_toggle':
                try:
                    self.eisenhower.open_calendar()
                    expanded = getattr(self.eisenhower.calendar_pane, "_expanded", False)
                    self.action_eis_calendario.setChecked(expanded)

                    if expanded:
                        self.action_eis_calendario.setText(QCoreApplication.translate("App","📅 Ocultar Calendário"))

                    else:
                        self.action_eis_calendario.setText(QCoreApplication.translate("App","📅 Mostrar Calendário"))

                except Exception:
                    pass

    except Exception as e:
        logger.error(f"Erro ao executar ação '{acao}' do módulo '{modulo}': {str(e)}", exc_info=True)
