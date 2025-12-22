from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QCalendarWidget, QComboBox, QListWidget, QListWidgetItem, QLabel, QAbstractItemView, QWidget
from PySide6.QtCore import Qt, QDate, QCoreApplication, QLocale, QSize, QObject, QEvent, QRect
from PySide6.QtGui import QPainter, QFontMetrics, QTextCharFormat, QBrush, QColor, QFont, QPalette
from PySide6.QtWidgets import QSizePolicy
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("App", text)


class LineEditFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(self._frame_width(), self._frame_width(), self._frame_width(), self._frame_width())

    def _frame_width(self) -> int:
        try:
            from PySide6.QtWidgets import QStyle
            return int(self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, None, self) or 1)

        except Exception:
            return 1

    def layout(self) -> QVBoxLayout:
        return self._layout

    def paintEvent(self, event):
        try:
            from PySide6.QtWidgets import QStyleOptionFrame, QStyle
            opt = QStyleOptionFrame()
            opt.initFrom(self)
            opt.rect = self.rect()
            opt.lineWidth = self._frame_width()
            opt.midLineWidth = 0

            painter = QPainter(self)
            self.style().drawPrimitive(QStyle.PE_FrameLineEdit, opt, painter, self)

        except Exception:
            return super().paintEvent(event)


class BadgeCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._task_counts = {}  # {date_iso_str: count}
        self._week_counts = {}  # {(year, week_number): count}
        self._month_counts = {}  # {(year, month): count}

    def set_task_counts(self, dates_list):
        try:
            from collections import Counter

            self._task_counts = Counter(dates_list)

            week_counter = Counter()
            for date_str in dates_list:
                qd = QDate.fromString(date_str, Qt.ISODate)
                if qd.isValid():
                    week_num = qd.weekNumber()[0]
                    year = qd.year()
                    week_counter[(year, week_num)] += 1

            self._week_counts = dict(week_counter)

            month_counter = Counter()
            for date_str in dates_list:
                qd = QDate.fromString(date_str, Qt.ISODate)
                if qd.isValid():
                    month_counter[(qd.year(), qd.month())] += 1

            self._month_counts = dict(month_counter)

            self.updateCells()

        except Exception as e:
            logger.error(f"Erro ao definir contadores de tarefas: {e}", exc_info=True)

    def paintCell(self, painter, rect, date):
        try:
            super().paintCell(painter, rect, date)

            date_iso = date.toString(Qt.ISODate)
            count = self._task_counts.get(date_iso, 0)

            if count > 0:
                self._draw_badge(painter, rect, count)

        except Exception as e:
            logger.error(f"Erro ao pintar célula do calendário: {e}", exc_info=True)

    def _draw_badge(self, painter, rect, count):
        try:
            painter.save()

            badge_size = 16
            padding = 2

            badge_x = rect.right() - badge_size - padding
            badge_y = rect.top() + padding
            badge_rect = QRect(badge_x, badge_y, badge_size, badge_size)

            pal = self.palette()
            badge_color = pal.highlight().color()

            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(badge_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(badge_rect)

            painter.setPen(pal.highlightedText().color())
            font = painter.font()
            font.setPixelSize(10)
            font.setBold(True)
            painter.setFont(font)

            count_text = str(count) if count < 100 else "99+"
            painter.drawText(badge_rect, Qt.AlignCenter, count_text)

            painter.restore()

        except Exception as e:
            logger.error(f"Erro ao desenhar badge: {e}", exc_info=True)


class CalendarDialog(QDialog):
    def __init__(self, app):
        super().__init__(app)
        try:
            self.app = app
            self.setModal(True)
            self.setWindowTitle(get_text("Calendário de Tarefas"))
            self._date_format = app.date_input.displayFormat() if hasattr(app, "date_input") else "dd/MM/yyyy"
            self._highlighted_dates = set()

            main_layout = QVBoxLayout(self)

            self.calendar = BadgeCalendarWidget(self)
            initial_date = app.date_input.date() if hasattr(app, "date_input") else QDate.currentDate()
            self.calendar.setSelectedDate(initial_date)

            hint = self.calendar.minimumSizeHint()
            fallback = QSize(300, 260)
            self.calendar.setMinimumSize(hint.expandedTo(fallback))
            self.calendar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

            self._apply_locale_to_calendar()

            self.calendar_frame = LineEditFrame(self)
            self.calendar_frame.layout().addWidget(self.calendar)
            main_layout.addWidget(self.calendar_frame)

            controls_layout = QHBoxLayout()
            self.filter_label = QLabel(get_text("Exibir por"), self)
            controls_layout.addWidget(self.filter_label)

            self.filter_combo = QComboBox(self)
            self.filter_combo.addItem(get_text("Dia"), "day")
            self.filter_combo.addItem(get_text("Semana"), "week")
            self.filter_combo.addItem(get_text("Mês"), "month")
            controls_layout.addWidget(self.filter_combo)
            controls_layout.addStretch()
            main_layout.addLayout(controls_layout)

            self.tasks_list = QListWidget(self)
            self.tasks_list.setSelectionMode(QAbstractItemView.NoSelection)
            self.tasks_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            main_layout.addWidget(self.tasks_list, 1)

            self.calendar.selectionChanged.connect(self.update_task_list)
            self.filter_combo.currentIndexChanged.connect(self.update_task_list)

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self._on_language_changed)

            self.update_task_list()

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

                def _sync_calendar_backgrounds():
                    try:
                        _apply_window_as_base(self.tasks_list)
                        _apply_window_as_base(self.filter_combo)

                    except Exception as e:
                        logger.debug(f"Falha ao sincronizar fundos do CalendarDialog via QPalette: {e}", exc_info=True)


                class _PaletteThemeSyncFilter(QObject):
                    def eventFilter(self, obj, event):
                        et = event.type()
                        if et in (QEvent.ApplicationPaletteChange, QEvent.PaletteChange, QEvent.ThemeChange):
                            _sync_calendar_backgrounds()

                        return super().eventFilter(obj, event)

                _sync_calendar_backgrounds()

                self._calendar_palette_sync_filter = _PaletteThemeSyncFilter(self)
                qt_app = QApplication.instance()
                if qt_app is not None:
                    qt_app.installEventFilter(self._calendar_palette_sync_filter)

            except Exception as e:
                logger.debug(f"Falha ao instalar sync de paleta (CalendarDialog): {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Erro ao inicializar CalendarDialog: {e}", exc_info=True)

    def closeEvent(self, event):
        try:
            if hasattr(self.app, "gerenciador_traducao"):
                try:
                    self.app.gerenciador_traducao.idioma_alterado.disconnect(self._on_language_changed)

                except (RuntimeError, TypeError):
                    pass

            super().closeEvent(event)

        except Exception as e:
            logger.error(f"Erro ao fechar CalendarDialog: {e}", exc_info=True)

    def _collect_tasks(self):
        try:
            tasks = []
            mapping = [
                (self.app.quadrant1_list, self.app.quadrant1_label.text(), False),
                (self.app.quadrant1_completed_list, f"{self.app.quadrant1_label.text()} - {self.app.quadrant1_completed_label.text()}", True),
                (self.app.quadrant2_list, self.app.quadrant2_label.text(), False),
                (self.app.quadrant2_completed_list, f"{self.app.quadrant2_label.text()} - {self.app.quadrant2_completed_label.text()}", True),
                (self.app.quadrant3_list, self.app.quadrant3_label.text(), False),
                (self.app.quadrant3_completed_list, f"{self.app.quadrant3_label.text()} - {self.app.quadrant3_completed_label.text()}", True),
                (self.app.quadrant4_list, self.app.quadrant4_label.text(), False),
                (self.app.quadrant4_completed_list, f"{self.app.quadrant4_label.text()} - {self.app.quadrant4_completed_label.text()}", True),
            ]
            for lst, category, completed in mapping:
                for i in range(lst.count()):
                    item = lst.item(i)
                    if not item or not (item.flags() & Qt.ItemIsSelectable):
                        continue

                    data = item.data(Qt.UserRole) or {}
                    text = data.get("text", item.text())
                    date_str = data.get("date")
                    time_str = data.get("time")
                    tasks.append({
                        "text": text,
                        "date": date_str,
                        "time": time_str,
                        "category": category,
                        "completed": completed
                    })

            return tasks

        except Exception as e:
            logger.error(f"Erro ao coletar tarefas do calendário: {e}", exc_info=True)
            return []

    def update_task_list(self):
        try:
            self.tasks_list.clear()
            self._apply_highlighted_dates()
            self._update_badge_counts()
            
            selected_date = self.calendar.selectedDate()
            filter_mode = self.filter_combo.currentData()
            filtered = []

            for task in self._collect_tasks():
                date_str = task.get("date")
                if not date_str:
                    continue

                qdate = QDate.fromString(date_str, Qt.ISODate)
                if not qdate.isValid():
                    continue

                if filter_mode == "day" and qdate != selected_date:
                    continue

                if filter_mode == "week":
                    selected_start_of_week = selected_date.addDays(-(selected_date.dayOfWeek() % 7))
                    task_start_of_week = qdate.addDays(-(qdate.dayOfWeek() % 7))
                    if selected_start_of_week != task_start_of_week:
                        continue

                if filter_mode == "month":
                    if qdate.month() != selected_date.month() or qdate.year() != selected_date.year():
                        continue

                filtered.append((qdate, task))

            if not filtered:
                placeholder = QListWidgetItem(get_text("Nenhuma tarefa para o período selecionado."))
                placeholder.setFlags((placeholder.flags() & ~Qt.ItemIsSelectable) & ~Qt.ItemIsEnabled)
                self.tasks_list.addItem(placeholder)
                return

            filtered.sort(key=lambda entry: (entry[0], entry[1]["time"] or "", entry[1]["text"].lower()))
            for qdate, task in filtered:
                status_text = get_text("Concluída") if task.get("completed") else get_text("Pendente")
                date_str = qdate.toString(self._date_format)
                time_str = task.get("time")
                if time_str:
                    dt_str = f"{date_str} {time_str}"

                else:
                    dt_str = date_str

                item_text = f"{dt_str} — {task['text']} — [{status_text}]"
                item = QListWidgetItem(item_text)
                item.setFlags((item.flags() & ~Qt.ItemIsSelectable) & ~Qt.ItemIsEnabled)
                self.tasks_list.addItem(item)

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de tarefas do calendário: {e}", exc_info=True)

    def _update_badge_counts(self):
        try:
            dates = []
            for task in self._collect_tasks():
                ds = task.get("date")
                if ds:
                    qd = QDate.fromString(ds, Qt.ISODate)
                    if qd.isValid():
                        dates.append(ds)

            self.calendar.set_task_counts(dates)

        except Exception as e:
            logger.error(f"Erro ao atualizar contadores de badges: {e}", exc_info=True)

    def _on_language_changed(self):
        try:
            self.setWindowTitle(get_text("Calendário de Tarefas"))
            self.filter_label.setText(get_text("Exibir por"))
            self.filter_combo.setItemText(0, get_text("Dia"))
            self.filter_combo.setItemText(1, get_text("Semana"))
            self.filter_combo.setItemText(2, get_text("Mês"))
            self._date_format = self.app.date_input.displayFormat() if hasattr(self.app, "date_input") else self._date_format

            self._apply_locale_to_calendar()
            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao atualizar idioma do calendário: {e}", exc_info=True)

    def _apply_locale_to_calendar(self):
        try:
            idioma = None
            if hasattr(self.app, "gerenciador_traducao"):
                idioma = self.app.gerenciador_traducao.obter_idioma_atual()

            if idioma and idioma.startswith("pt"):
                locale = QLocale(QLocale.Portuguese, QLocale.Brazil)

            elif idioma and idioma.startswith("en"):
                locale = QLocale(QLocale.English, QLocale.UnitedStates)

            else:
                locale = QLocale.system()

            self.calendar.setLocale(locale)
            self.calendar.setFirstDayOfWeek(Qt.Sunday)

        except Exception as e:
            logger.error(f"Erro ao aplicar localidade no calendário: {e}", exc_info=True)

    def _get_task_dates(self):
        dates = set()
        try:
            for task in self._collect_tasks():
                ds = task.get("date")
                if not ds:
                    continue

                qd = QDate.fromString(ds, Qt.ISODate)
                if qd.isValid():
                    dates.add(qd.toString(Qt.ISODate))

        except Exception as e:
            logger.error(f"Erro ao obter datas das tarefas do calendário: {e}", exc_info=True)

        return dates

    def _apply_highlighted_dates(self):
        try:
            new_dates = self._get_task_dates()
            if not hasattr(self, "_highlighted_dates"):
                self._highlighted_dates = set()

            to_clear = self._highlighted_dates - new_dates
            if to_clear:
                blank = QTextCharFormat()
                for ds in to_clear:
                    qd = QDate.fromString(ds, Qt.ISODate)
                    if qd.isValid():
                        self.calendar.setDateTextFormat(qd, blank)

            fmt = QTextCharFormat()
            pal = self.palette()
            base = pal.highlight().color()
            color = QColor(base.red(), base.green(), base.blue(), 60)
            fmt.setBackground(QBrush(color))
            fmt.setFontWeight(QFont.Bold)

            for ds in new_dates:
                qd = QDate.fromString(ds, Qt.ISODate)
                if qd.isValid():
                    self.calendar.setDateTextFormat(qd, fmt)

            self._highlighted_dates = new_dates

        except Exception as e:
            logger.error(f"Erro ao aplicar destaque nas datas do calendário: {e}", exc_info=True)


class RotatedTabButton(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        try:
            self._text = text
            self.setMinimumWidth(25)
            self._recompute_size()

        except Exception as e:
            logger.error(f"Erro ao inicializar RotatedTabButton: {e}", exc_info=True)

    def setText(self, text):
        try:
            self._text = text
            self._recompute_size()
            self.update()

        except Exception as e:
            logger.error(f"Erro ao definir texto do botão de aba: {e}", exc_info=True)

    def text(self):
        try:
            return self._text

        except Exception as e:
            logger.error(f"Erro ao obter texto do botão de aba: {e}", exc_info=True)

    def _recompute_size(self):
        try:
            fm = QFontMetrics(self.font())
            text_w = fm.horizontalAdvance(self._text)
            text_h = fm.height()
            width = text_h + 5
            height = text_w + 20
            self.setFixedSize(QSize(width, height))

        except Exception as e:
            logger.error(f"Erro ao recalcular tamanho do botão de aba: {e}", exc_info=True)

    def mousePressEvent(self, event):
        try:
            self.parent().toggle_panel()
            super().mousePressEvent(event)

        except Exception as e:
            logger.error(f"Erro ao processar evento de clique no botão de aba: {e}", exc_info=True)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.save()
            painter.fillRect(self.rect(), self.palette().button().color())
            painter.setPen(self.palette().dark().color())
            painter.drawRect(0, 0, self.width()-1, self.height()-1)
            painter.translate(0, self.height())
            painter.rotate(270)
            fm = painter.fontMetrics()
            text_w = fm.horizontalAdvance(self._text)
            x = (self.height() - text_w) / 2
            y = (self.width() + fm.ascent() - fm.descent()) / 2
            painter.setPen(self.palette().buttonText().color())
            painter.drawText(x, y, self._text)
            painter.restore()

        except Exception as e:
            logger.error(f"Erro ao pintar botão de aba: {e}", exc_info=True)


class CalendarPanel(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        try:
            self.app = app
            self._date_format = app.date_input.displayFormat() if hasattr(app, "date_input") else "dd/MM/yyyy"
            self._highlighted_dates = set()

            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(5, 1, 5, 9)
            main_layout.setSpacing(6)

            self.calendar = BadgeCalendarWidget(self)
            initial_date = app.date_input.date() if hasattr(app, "date_input") else QDate.currentDate()
            self.calendar.setSelectedDate(initial_date)
            hint = self.calendar.minimumSizeHint()
            fallback = QSize(300, 260)
            self.calendar.setMinimumSize(hint.expandedTo(fallback))
            self.calendar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self._apply_locale_to_calendar()

            self.calendar_frame = LineEditFrame(self)
            self.calendar_frame.layout().addWidget(self.calendar)
            main_layout.addWidget(self.calendar_frame)

            controls_layout = QHBoxLayout()
            self.filter_label = QLabel(get_text("Exibir por"), self)
            controls_layout.addWidget(self.filter_label)

            self.filter_combo = QComboBox(self)
            self.filter_combo.addItem(get_text("Dia"), "day")
            self.filter_combo.addItem(get_text("Semana"), "week")
            self.filter_combo.addItem(get_text("Mês"), "month")
            controls_layout.addWidget(self.filter_combo)
            controls_layout.addStretch()
            main_layout.addLayout(controls_layout)

            self.tasks_list = QListWidget(self)
            self.tasks_list.setSelectionMode(QAbstractItemView.NoSelection)
            self.tasks_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            main_layout.addWidget(self.tasks_list, 1)

            self.calendar.selectionChanged.connect(self.update_task_list)
            self.filter_combo.currentIndexChanged.connect(self.update_task_list)

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self._on_language_changed)

            self.update_task_list()

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

                def _sync_calendar_panel_backgrounds():
                    try:
                        _apply_window_as_base(self.tasks_list)
                        _apply_window_as_base(self.filter_combo)

                    except Exception as e:
                        logger.debug(f"Falha ao sincronizar fundos do CalendarPanel via QPalette: {e}", exc_info=True)


                class _PaletteThemeSyncFilter(QObject):
                    def eventFilter(self, obj, event):
                        et = event.type()
                        if et in (QEvent.ApplicationPaletteChange, QEvent.PaletteChange, QEvent.ThemeChange):
                            _sync_calendar_panel_backgrounds()

                        return super().eventFilter(obj, event)

                _sync_calendar_panel_backgrounds()

                self._calendar_panel_palette_sync_filter = _PaletteThemeSyncFilter(self)
                qt_app = QApplication.instance()
                if qt_app is not None:
                    qt_app.installEventFilter(self._calendar_panel_palette_sync_filter)

            except Exception as e:
                logger.debug(f"Falha ao instalar sync de paleta (CalendarPanel): {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Erro ao inicializar CalendarPanel: {e}", exc_info=True)

    def _collect_tasks(self):
        try:
            return CalendarDialog._collect_tasks(self)

        except Exception as e:
            logger.error(f"Erro ao coletar tarefas: {e}", exc_info=True)

    def update_task_list(self):
        try:
            return CalendarDialog.update_task_list(self)

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de tarefas: {e}", exc_info=True)

    def _update_badge_counts(self):
        try:
            return CalendarDialog._update_badge_counts(self)

        except Exception as e:
            logger.error(f"Erro ao atualizar contadores de badges: {e}", exc_info=True)

    def _get_task_dates(self):
        try:
            return CalendarDialog._get_task_dates(self)

        except Exception as e:
            logger.error(f"Erro ao obter datas de tarefas: {e}", exc_info=True)

    def _apply_highlighted_dates(self):
        try:
            return CalendarDialog._apply_highlighted_dates(self)

        except Exception as e:
            logger.error(f"Erro ao aplicar datas destacadas: {e}", exc_info=True)

    def _on_language_changed(self):
        try:
            self.filter_label.setText(get_text("Exibir por"))
            self.filter_combo.setItemText(0, get_text("Dia"))
            self.filter_combo.setItemText(1, get_text("Semana"))
            self.filter_combo.setItemText(2, get_text("Mês"))
            self._date_format = self.app.date_input.displayFormat() if hasattr(self.app, "date_input") else self._date_format
            self._apply_locale_to_calendar()
            self.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao atualizar idioma do painel de calendário: {e}", exc_info=True)

    def _apply_locale_to_calendar(self):
        try:
            return CalendarDialog._apply_locale_to_calendar(self)

        except Exception as e:
            logger.error(f"Erro ao aplicar locale ao calendário: {e}", exc_info=True)


class Calendar(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        try:
            self.app = app
            self._expanded = False
            self._panel_width = 360

            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 11, 0, 0)
            layout.setSpacing(0)

            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

            self.toggle_button = RotatedTabButton(get_text("Mostrar Calendário"), self)
            self.toggle_button.setMinimumWidth(25)
            layout.addWidget(self.toggle_button, 0, Qt.AlignLeft | Qt.AlignTop)

            self.calendar_panel = CalendarPanel(app, self)
            self.calendar_panel.setFixedWidth(self._panel_width)
            self.calendar_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            layout.addWidget(self.calendar_panel, 1)

            self.calendar_panel.setVisible(False)
            self._apply_fixed_width()

            if hasattr(self.app, "gerenciador_traducao"):
                self.app.gerenciador_traducao.idioma_alterado.connect(self.on_language_changed)

        except Exception as e:
            logger.error(f"Erro ao inicializar Calendar: {e}", exc_info=True)

    def _apply_fixed_width(self):
        try:
            btn_w = self.toggle_button.width()
            total = btn_w + (self._panel_width if self._expanded else 0)
            self.setFixedWidth(total)

        except Exception as e:
            logger.error(f"Erro ao aplicar largura fixa: {e}", exc_info=True)

    def toggle_panel(self, open_if_hidden=False):
        try:
            previous = self._expanded
            if open_if_hidden and not self._expanded:
                self._expanded = True

            else:
                self._expanded = not self._expanded

            self.calendar_panel.setVisible(self._expanded)

            if self._expanded:
                hint_w = max(self.calendar_panel.sizeHint().width(), 300)
                self._panel_width = max(self._panel_width, hint_w)
                self.calendar_panel.setFixedWidth(self._panel_width)
                self.toggle_button.setText(get_text("Recolher Calendário"))

            else:
                self.toggle_button.setText(get_text("Mostrar Calendário"))

            self._apply_fixed_width()

            try:
                main_win = getattr(self, "app", None)
                if not main_win:
                    return

                if main_win.isMaximized():
                    try:
                        central = main_win.centralWidget()
                        if central:
                            central.updateGeometry()

                    except Exception:
                        pass

                    main_win.update()
                    return

                avail_w = None
                try:
                    wh = main_win.windowHandle()
                    if wh and wh.screen():
                        avail_w = wh.screen().availableGeometry().width()

                except Exception:
                    avail_w = None

                if avail_w is None:
                    try:
                        avail_w = main_win.screen().availableGeometry().width()

                    except Exception:
                        avail_w = 99999

                if self._expanded and not previous:
                    desired = main_win.width() + self._panel_width
                    new_w = min(desired, avail_w)
                    main_win.resize(new_w, main_win.height())

                elif (not self._expanded) and previous:
                    new_w = max(400, main_win.width() - self._panel_width)
                    main_win.resize(new_w, main_win.height())

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao alternar painel de calendário: {e}", exc_info=True)

    def on_language_changed(self):
        try:
            self.toggle_button.setText(get_text("Recolher Calendário") if self._expanded else get_text("Mostrar Calendário"))
            try:
                self.calendar_panel._on_language_changed()

            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao atualizar idioma do calendário: {e}", exc_info=True)
