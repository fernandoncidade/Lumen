from PySide6.QtGui import QIcon, QPalette
from PySide6.QtCore import Qt, QCoreApplication, QDate, QLocale, QTime, QObject, QEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QComboBox, QDateEdit, QCheckBox, QTimeEdit
from source.utils.IconUtils import get_icon_path
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("App", text)


class CustomTimeEdit(QTimeEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWrapping(True)
        self._last_time = self.time()

    def stepBy(self, steps):
        current_time = self.time()
        current_section = self.currentSection()

        if current_section == QTimeEdit.MinuteSection:
            total_minutes = current_time.hour() * 60 + current_time.minute()
            total_minutes += steps

            if total_minutes < 0:
                total_minutes = 1439

            elif total_minutes >= 1440:
                total_minutes = 0

            new_hour = total_minutes // 60
            new_minute = total_minutes % 60
            new_time = QTime(new_hour, new_minute, current_time.second())
            self.setTime(new_time)

        else:
            super().stepBy(steps)

        self._last_time = self.time()


class DragDropTaskList(QListWidget):
    def __init__(self, app, is_completed_list: bool, parent=None):
        super().__init__(parent)
        self._app = app
        self._is_completed_list = bool(is_completed_list)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QListWidget.DragDrop)

        try:
            from PySide6.QtWidgets import QAbstractItemView
            self.setSelectionMode(QAbstractItemView.SingleSelection)

        except Exception:
            pass

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                it = self.itemAt(event.pos())
                if it and (it.flags() & Qt.ItemIsSelectable):
                    self.setCurrentItem(it)
                    self.clearSelection()
                    it.setSelected(True)

        except Exception:
            pass

        return super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        try:
            event.acceptProposedAction()

        except Exception:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        try:
            event.acceptProposedAction()

        except Exception:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        try:
            source = event.source()

            if source is self:
                super().dropEvent(event)
                try:
                    if hasattr(self._app, "save_tasks"):
                        self._app.save_tasks()

                    if hasattr(self._app, "calendar_pane") and self._app.calendar_pane:
                        self._app.calendar_pane.calendar_panel.update_task_list()

                except Exception:
                    pass

                return

            if not isinstance(source, QListWidget):
                event.ignore()
                return

            items = list(source.selectedItems() or [])
            if not items:
                event.ignore()
                return

            new_state = Qt.Checked if self._is_completed_list else Qt.Unchecked

            source.blockSignals(True)
            self.blockSignals(True)
            try:
                for it in items:
                    if not it:
                        continue

                    if not (it.flags() & Qt.ItemIsSelectable):
                        continue

                    self._app.move_item_between_lists(it, source, self, new_state)

            finally:
                source.blockSignals(False)
                self.blockSignals(False)

            try:
                source.clearSelection()

            except Exception:
                pass

            try:
                if hasattr(self._app, "save_tasks"):
                    self._app.save_tasks()

                if hasattr(self._app, "calendar_pane") and self._app.calendar_pane:
                    self._app.calendar_pane.calendar_panel.update_task_list()

            except Exception:
                pass

            event.setDropAction(Qt.CopyAction)
            event.accept()

        except Exception as e:
            logger.error(f"Erro no dropEvent (drag&drop Eisenhower): {e}", exc_info=True)
            try:
                super().dropEvent(event)

            except Exception:
                pass

def init_ui(app):
    app.main_layout = QVBoxLayout()
    input_layout = QHBoxLayout()

    app.task_input = QLineEdit(app)
    app.task_input.setPlaceholderText(get_text("Adicione uma tarefa..."))
    input_layout.addWidget(app.task_input)

    app.date_checkbox = QCheckBox(get_text("Vincular data"))
    app.date_checkbox.setChecked(True)
    input_layout.addWidget(app.date_checkbox)

    app.date_input = QDateEdit(app)
    app.date_input.setCalendarPopup(True)
    app.date_input.setDate(QDate.currentDate())

    def _apply_locale_to_date_input():
        locale = QLocale.system()
        try:
            if hasattr(app, "gerenciador_traducao"):
                idioma = app.gerenciador_traducao.obter_idioma_atual()
                if idioma and idioma.startswith("pt"):
                    locale = QLocale(QLocale.Portuguese, QLocale.Brazil)

                elif idioma and idioma.startswith("en"):
                    locale = QLocale(QLocale.English, QLocale.UnitedStates)

        except Exception as e:
            logger.error(f"Erro ao aplicar locale à data: {e}", exc_info=True)
            locale = QLocale.system()

        app.date_input.setLocale(locale)
        try:
            fmt = locale.dateFormat(QLocale.ShortFormat)

        except Exception as e:
            logger.error(f"Erro ao obter formato de data: {e}", exc_info=True)
            fmt = "dd/MM/yyyy"

        try:
            import re
            fmt = re.sub(r'(?<!y)yy(?!y)', 'yyyy', fmt)

        except Exception as e:
            logger.error(f"Erro ao ajustar formato de data: {e}", exc_info=True)

        app.date_input.setDisplayFormat(fmt)

    _apply_locale_to_date_input()

    if hasattr(app, "gerenciador_traducao"):
        try:
            app.gerenciador_traducao.idioma_alterado.connect(lambda _: _apply_locale_to_date_input())

        except Exception as e:
            logger.error(f"Erro ao conectar sinal de idioma_alterado para data: {e}", exc_info=True)

    input_layout.addWidget(app.date_input)

    app.time_checkbox = QCheckBox(get_text("Vincular horário"))
    app.time_checkbox.setChecked(True)
    input_layout.addWidget(app.time_checkbox)

    app.time_input = CustomTimeEdit(app)
    app.time_input.setDisplayFormat("HH:mm")
    app.time_input.setEnabled(True)
    input_layout.addWidget(app.time_input)

    def _apply_locale_to_time_input():
        try:
            app.time_input.setDisplayFormat("HH:mm")

        except Exception as e:
            logger.error(f"Erro ao aplicar locale ao horário: {e}", exc_info=True)

    _apply_locale_to_time_input()

    if hasattr(app, "gerenciador_traducao"):
        try:
            app.gerenciador_traducao.idioma_alterado.connect(lambda _: _apply_locale_to_time_input())
            app.gerenciador_traducao.idioma_alterado.connect(lambda _: app.time_checkbox.setText(get_text("Vincular horário")))

        except Exception as e:
            logger.error(f"Erro ao conectar sinal de idioma_alterado para horário: {e}", exc_info=True)

    def _on_time_checkbox_toggled(checked: bool):
        try:
            app.time_input.setEnabled(checked and app.date_checkbox.isChecked())

        except Exception as e:
            logger.error(f"Erro ao alternar checkbox de horário: {e}", exc_info=True)

    def _on_date_checkbox_toggled(checked: bool):
        try:
            app.time_checkbox.setEnabled(checked)
            app.time_input.setEnabled(checked and app.time_checkbox.isChecked())
            if not checked:
                app.time_checkbox.setChecked(False)

        except Exception as e:
            logger.error(f"Erro ao alternar checkbox de data: {e}", exc_info=True)

    app.time_checkbox.toggled.connect(_on_time_checkbox_toggled)
    app.date_checkbox.toggled.connect(_on_date_checkbox_toggled)
    app.time_checkbox.setEnabled(app.date_checkbox.isChecked())

    app.quadrant_selector = QComboBox(app)
    app.quadrant_selector.addItems([
        get_text("Importante e Urgente"),
        get_text("Importante, mas Não Urgente"),
        get_text("Não Importante, mas Urgente"),
        get_text("Não Importante e Não Urgente")
    ])
    input_layout.addWidget(app.quadrant_selector)

    app.add_button = QPushButton(get_text("Adicionar Tarefa"))
    add_icon_path = get_icon_path("organizador.png")
    if add_icon_path:
        app.add_button.setIcon(QIcon(add_icon_path))

    app.add_button.clicked.connect(app.add_task)
    input_layout.addWidget(app.add_button)

    app.calendar_button = QPushButton(get_text("Calendário"))
    add_icon_path = get_icon_path("calendar.png")
    if add_icon_path:
        app.calendar_button.setIcon(QIcon(add_icon_path))

    app.calendar_button.clicked.connect(app.open_calendar)
    input_layout.addWidget(app.calendar_button)

    app.main_layout.addLayout(input_layout)

    quadrant_layout = QHBoxLayout()

    app.quadrant1_layout = QVBoxLayout()
    app.quadrant1_label = QLabel(get_text("Importante e Urgente"))
    app.quadrant1_list = DragDropTaskList(app, is_completed_list=False)
    app.add_placeholder(app.quadrant1_list, get_text("1º Quadrante"))
    app.quadrant1_completed_label = QLabel(get_text("Concluídas"))
    app.quadrant1_completed_list = DragDropTaskList(app, is_completed_list=True)
    app.add_placeholder(app.quadrant1_completed_list, get_text("Nenhuma Tarefa Concluída"))
    app.quadrant1_layout.addWidget(app.quadrant1_label)
    app.quadrant1_layout.addWidget(app.quadrant1_list)
    app.quadrant1_layout.addWidget(app.quadrant1_completed_label)
    app.quadrant1_layout.addWidget(app.quadrant1_completed_list)

    app.quadrant2_layout = QVBoxLayout()
    app.quadrant2_label = QLabel(get_text("Importante, mas Não Urgente"))
    app.quadrant2_list = DragDropTaskList(app, is_completed_list=False)
    app.add_placeholder(app.quadrant2_list, get_text("2º Quadrante"))
    app.quadrant2_completed_label = QLabel(get_text("Concluídas"))
    app.quadrant2_completed_list = DragDropTaskList(app, is_completed_list=True)
    app.add_placeholder(app.quadrant2_completed_list, get_text("Nenhuma Tarefa Concluída"))
    app.quadrant2_layout.addWidget(app.quadrant2_label)
    app.quadrant2_layout.addWidget(app.quadrant2_list)
    app.quadrant2_layout.addWidget(app.quadrant2_completed_label)
    app.quadrant2_layout.addWidget(app.quadrant2_completed_list)

    app.quadrant3_layout = QVBoxLayout()
    app.quadrant3_label = QLabel(get_text("Não Importante, mas Urgente"))
    app.quadrant3_list = DragDropTaskList(app, is_completed_list=False)
    app.add_placeholder(app.quadrant3_list, get_text("3º Quadrante"))
    app.quadrant3_completed_label = QLabel(get_text("Concluídas"))
    app.quadrant3_completed_list = DragDropTaskList(app, is_completed_list=True)
    app.add_placeholder(app.quadrant3_completed_list, get_text("Nenhuma Tarefa Concluída"))
    app.quadrant3_layout.addWidget(app.quadrant3_label)
    app.quadrant3_layout.addWidget(app.quadrant3_list)
    app.quadrant3_layout.addWidget(app.quadrant3_completed_label)
    app.quadrant3_layout.addWidget(app.quadrant3_completed_list)

    app.quadrant4_layout = QVBoxLayout()
    app.quadrant4_label = QLabel(get_text("Não Importante e Não Urgente"))
    app.quadrant4_list = DragDropTaskList(app, is_completed_list=False)
    app.add_placeholder(app.quadrant4_list, get_text("4º Quadrante"))
    app.quadrant4_completed_label = QLabel(get_text("Concluídas"))
    app.quadrant4_completed_list = DragDropTaskList(app, is_completed_list=True)
    app.add_placeholder(app.quadrant4_completed_list, get_text("Nenhuma Tarefa Concluída"))
    app.quadrant4_layout.addWidget(app.quadrant4_label)
    app.quadrant4_layout.addWidget(app.quadrant4_list)
    app.quadrant4_layout.addWidget(app.quadrant4_completed_label)
    app.quadrant4_layout.addWidget(app.quadrant4_completed_list)

    quadrant_layout.addLayout(app.quadrant1_layout)
    quadrant_layout.addLayout(app.quadrant2_layout)
    quadrant_layout.addLayout(app.quadrant3_layout)
    quadrant_layout.addLayout(app.quadrant4_layout)

    app.main_layout.addLayout(quadrant_layout)

    container = QWidget()
    container.setLayout(app.main_layout)

    if hasattr(app, "setCentralWidget"):
        app.setCentralWidget(container)

    else:
        app._root_widget = container

    app.quadrant1_list.itemChanged.connect(lambda item: app.handle_item_checked(item, app.quadrant1_list, app.quadrant1_completed_list))
    app.quadrant2_list.itemChanged.connect(lambda item: app.handle_item_checked(item, app.quadrant2_list, app.quadrant2_completed_list))
    app.quadrant3_list.itemChanged.connect(lambda item: app.handle_item_checked(item, app.quadrant3_list, app.quadrant3_completed_list))
    app.quadrant4_list.itemChanged.connect(lambda item: app.handle_item_checked(item, app.quadrant4_list, app.quadrant4_completed_list))

    app.quadrant1_completed_list.itemChanged.connect(lambda item: app.handle_item_checked(item, app.quadrant1_completed_list, app.quadrant1_list))
    app.quadrant2_completed_list.itemChanged.connect(lambda item: app.handle_item_checked(item, app.quadrant2_completed_list, app.quadrant2_list))
    app.quadrant3_completed_list.itemChanged.connect(lambda item: app.handle_item_checked(item, app.quadrant3_completed_list, app.quadrant3_list))
    app.quadrant4_completed_list.itemChanged.connect(lambda item: app.handle_item_checked(item, app.quadrant4_completed_list, app.quadrant4_list))

    for lst in (
        app.quadrant1_list, app.quadrant2_list, app.quadrant3_list, app.quadrant4_list,
        app.quadrant1_completed_list, app.quadrant2_completed_list, app.quadrant3_completed_list, app.quadrant4_completed_list
    ):
        lst.setContextMenuPolicy(Qt.CustomContextMenu)
        lst.customContextMenuRequested.connect(lambda point, l=lst: app.show_context_menu(point, l))

    try:
        from PySide6.QtWidgets import QApplication

        def _apply_window_as_base(widget):
            if widget is None:
                return

            qt_app = QApplication.instance()
            if qt_app is None:
                return

            window_color = qt_app.palette().color(QPalette.Window)

            pal = widget.palette()
            pal.setColor(QPalette.Base, window_color)
            pal.setColor(QPalette.AlternateBase, window_color)

            try:
                if isinstance(widget, QComboBox):
                    pal.setColor(QPalette.Button, window_color)

            except Exception:
                pass

            widget.setPalette(pal)

            vp = getattr(widget, "viewport", None)
            if callable(vp):
                try:
                    widget.viewport().setAutoFillBackground(True)
                    widget.viewport().setPalette(pal)

                except Exception:
                    pass

            else:
                try:
                    widget.setAutoFillBackground(True)

                except Exception:
                    pass

            view = getattr(widget, "view", None)
            if callable(view):
                try:
                    v = view()
                    if v is not None:
                        v.setPalette(pal)
                        try:
                            v.viewport().setAutoFillBackground(True)
                            v.viewport().setPalette(pal)

                        except Exception:
                            pass

                except Exception:
                    pass

        def _sync_eisenhower_backgrounds():
            try:
                _apply_window_as_base(app.task_input)
                _apply_window_as_base(app.quadrant_selector)

                for w in (
                    app.quadrant1_list,
                    app.quadrant2_list,
                    app.quadrant3_list,
                    app.quadrant4_list,
                    app.quadrant1_completed_list,
                    app.quadrant2_completed_list,
                    app.quadrant3_completed_list,
                    app.quadrant4_completed_list,
                ):
                    _apply_window_as_base(w)

            except Exception as e:
                logger.debug(f"Falha ao sincronizar fundos da Matriz Eisenhower via QPalette: {e}", exc_info=True)


        class _PaletteThemeSyncFilter(QObject):
            def eventFilter(self, obj, event):
                et = event.type()
                tipos = (
                    QEvent.ApplicationPaletteChange,
                    QEvent.PaletteChange,
                    QEvent.StyleChange,
                    QEvent.ThemeChange,
                )

                try:
                    tipos = tipos + (QEvent.ColorSchemeChange,)

                except AttributeError:
                    pass

                if et in tipos:
                    _sync_eisenhower_backgrounds()

                return super().eventFilter(obj, event)

        _sync_eisenhower_backgrounds()

        app._eisenhower_palette_sync_filter = _PaletteThemeSyncFilter(app)
        qt_app = QApplication.instance()
        if qt_app is not None:
            qt_app.installEventFilter(app._eisenhower_palette_sync_filter)

    except Exception as e:
        logger.debug(f"Falha ao instalar sync de paleta (Eisenhower): {e}", exc_info=True)
