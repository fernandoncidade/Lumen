from PySide6.QtWidgets import (QMenu, QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, 
                               QDateEdit, QTimeEdit, QCheckBox, QDialogButtonBox, QCalendarWidget)
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication, Qt, QDate, QTime, QLocale
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("App", text)

def _effective_locale(app) -> QLocale:
    try:
        if hasattr(app, "date_input") and app.date_input is not None:
            return app.date_input.locale()

    except Exception:
        pass

    try:
        if hasattr(app, "gerenciador_traducao"):
            idioma = app.gerenciador_traducao.obter_idioma_atual()
            if idioma and idioma.startswith("pt"):
                return QLocale(QLocale.Portuguese, QLocale.Brazil)

            if idioma and idioma.startswith("en"):
                return QLocale(QLocale.English, QLocale.UnitedStates)

    except Exception:
        pass

    return QLocale.system()

def _apply_locale_to_dateedit(app, de: QDateEdit):
    try:
        loc = _effective_locale(app)
        de.setLocale(loc)

        cw = de.calendarWidget()
        if cw is None:
            cw = QCalendarWidget(de)
            de.setCalendarWidget(cw)

        cw.setLocale(loc)

        cw.update()
        de.update()

    except Exception as e:
        logger.debug(f"Falha ao aplicar locale no calendário do QDateEdit: {e}", exc_info=True)

def _is_completed_list(app, lst) -> bool:
    return lst in (
        app.quadrant1_completed_list,
        app.quadrant2_completed_list,
        app.quadrant3_completed_list,
        app.quadrant4_completed_list,
    )

def _quadrant_options(app):
    return [
        app.quadrant1_label.text(),
        app.quadrant2_label.text(),
        app.quadrant3_label.text(),
        app.quadrant4_label.text(),
    ]

def _target_list_for_quadrant(app, quadrant_index: int, keep_completed: bool):
    pending = [app.quadrant1_list, app.quadrant2_list, app.quadrant3_list, app.quadrant4_list]
    done = [app.quadrant1_completed_list, app.quadrant2_completed_list, app.quadrant3_completed_list, app.quadrant4_completed_list]
    if 0 <= quadrant_index < 4:
        return done[quadrant_index] if keep_completed else pending[quadrant_index]

    return None

def _base_text_from_item(item) -> str:
    data = item.data(Qt.UserRole) or {}
    base = (data.get("text") or "").strip()
    if base:
        return base

    txt = (item.text() or "").strip()
    if " — " in txt:
        return txt.split(" — ", 1)[0].strip()

    return txt

def _build_display_and_tooltip(app, base_text: str, date_iso: str | None, time_str: str | None):
    display_text = base_text
    tooltip_lines = []

    if date_iso:
        qd = QDate.fromString(date_iso, Qt.ISODate)
        if qd.isValid():
            date_human = qd.toString(app.date_input.displayFormat())
            if time_str:
                display_text = f"{base_text} — {date_human} {time_str}"

            else:
                display_text = f"{base_text} — {date_human}"

            tooltip_lines.append(f"{get_text('Data') or 'Data'}: {date_human}")

    if time_str:
        tooltip_lines.append(f"{get_text('Horário') or 'Horário'}: {time_str}")

    return display_text, ("\n".join(tooltip_lines) if tooltip_lines else "")

def _edit_date_time_dialog(app, item):
    try:
        data = item.data(Qt.UserRole) or {}
        current_date_iso = data.get("date")
        current_time = data.get("time")

        dlg = QDialog(app)
        dlg.setWindowTitle(get_text("Editar data/horário"))
        layout = QVBoxLayout(dlg)

        row_date = QHBoxLayout()
        cb_date = QCheckBox(get_text("Vincular data"), dlg)
        de = QDateEdit(dlg)
        de.setCalendarPopup(True)
        de.setDisplayFormat(app.date_input.displayFormat() if hasattr(app, "date_input") else "dd/MM/yyyy")
        de.setDate(QDate.currentDate())

        _apply_locale_to_dateedit(app, de)

        if current_date_iso:
            qd = QDate.fromString(current_date_iso, Qt.ISODate)
            if qd.isValid():
                cb_date.setChecked(True)
                de.setDate(qd)

            else:
                cb_date.setChecked(False)

        else:
            cb_date.setChecked(False)

        de.setEnabled(cb_date.isChecked())
        cb_date.toggled.connect(de.setEnabled)

        row_date.addWidget(cb_date)
        row_date.addWidget(de)
        layout.addLayout(row_date)

        row_time = QHBoxLayout()
        cb_time = QCheckBox(get_text("Vincular horário"), dlg)
        te = QTimeEdit(dlg)
        te.setDisplayFormat("HH:mm")
        te.setTime(QTime.currentTime())

        if current_time:
            qt = QTime.fromString(current_time, "HH:mm")
            if qt.isValid():
                cb_time.setChecked(True)
                te.setTime(qt)

            else:
                cb_time.setChecked(False)

        else:
            cb_time.setChecked(False)

        def _sync_time_enabled():
            te.setEnabled(cb_date.isChecked() and cb_time.isChecked())

        cb_time.toggled.connect(lambda _: _sync_time_enabled())
        cb_date.toggled.connect(lambda _: _sync_time_enabled())
        _sync_time_enabled()

        row_time.addWidget(cb_time)
        row_time.addWidget(te)
        layout.addLayout(row_time)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dlg)

        try:
            ok_btn = buttons.button(QDialogButtonBox.Ok)
            cancel_btn = buttons.button(QDialogButtonBox.Cancel)
            if ok_btn:
                ok_btn.setText(get_text("OK"))

            if cancel_btn:
                cancel_btn.setText(get_text("Cancelar"))

        except Exception:
            pass

        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        try:
            if hasattr(app, "gerenciador_traducao"):
                def _on_idioma_alterado(_=None):
                    dlg.setWindowTitle(get_text("Editar data/horário"))
                    cb_date.setText(get_text("Vincular data"))
                    cb_time.setText(get_text("Vincular horário"))
                    _apply_locale_to_dateedit(app, de)

                    try:
                        ok_btn = buttons.button(QDialogButtonBox.Ok)
                        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
                        if ok_btn:
                            ok_btn.setText(get_text("OK"))

                        if cancel_btn:
                            cancel_btn.setText(get_text("Cancelar"))

                    except Exception:
                        pass

                app.gerenciador_traducao.idioma_alterado.connect(_on_idioma_alterado)

        except Exception:
            pass

        if dlg.exec() != QDialog.Accepted:
            return

        new_date_iso = None
        new_time_str = None

        if cb_date.isChecked():
            new_date_iso = de.date().toString(Qt.ISODate)
            if cb_time.isChecked():
                new_time_str = te.time().toString("HH:mm")

        base_text = _base_text_from_item(item)
        display_text, tooltip = _build_display_and_tooltip(app, base_text, new_date_iso, new_time_str)

        new_data = dict(data) if isinstance(data, dict) else {}
        new_data["text"] = base_text
        new_data["date"] = new_date_iso
        new_data["time"] = new_time_str

        lst = item.listWidget()
        if lst is None:
            return

        row = lst.row(item)
        check_state = item.checkState()

        lst.takeItem(row)
        try:
            if hasattr(app, "cleanup_time_groups"):
                app.cleanup_time_groups(lst)

        except Exception:
            pass

        from PySide6.QtWidgets import QListWidgetItem
        new_item = QListWidgetItem(display_text)
        new_item.setFlags(new_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        new_item.setCheckState(check_state)
        new_item.setData(Qt.UserRole, new_data)
        if tooltip:
            new_item.setToolTip(tooltip)

        if hasattr(app, "insert_task_into_quadrant_list"):
            app.insert_task_into_quadrant_list(lst, new_item)

        else:
            lst.addItem(new_item)

        try:
            if hasattr(app, "cleanup_time_groups"):
                app.cleanup_time_groups(lst)

        except Exception:
            pass

        app.save_tasks()
        if hasattr(app, "calendar_pane") and app.calendar_pane:
            app.calendar_pane.calendar_panel.update_task_list()

    except Exception as e:
        logger.error(f"Erro ao editar data/horário via menu: {e}", exc_info=True)

def _move_to_quadrant(app, item, source_list):
    try:
        opts = _quadrant_options(app)
        chosen, ok = QInputDialog.getItem(
            app,
            get_text("Mover tarefa"),
            get_text("Selecione o quadrante:"),
            opts,
            0,
            False
        )
        if not ok or not chosen:
            return

        try:
            idx = opts.index(chosen)

        except ValueError:
            return

        keep_completed = _is_completed_list(app, source_list)
        target = _target_list_for_quadrant(app, idx, keep_completed=keep_completed)
        if target is None or target is source_list:
            return

        new_state = Qt.Checked if keep_completed else Qt.Unchecked

        source_list.blockSignals(True)
        target.blockSignals(True)
        try:
            app.move_item_between_lists(item, source_list, target, new_state)

        finally:
            source_list.blockSignals(False)
            target.blockSignals(False)

        app.save_tasks()
        if hasattr(app, "calendar_pane") and app.calendar_pane:
            app.calendar_pane.calendar_panel.update_task_list()

    except Exception as e:
        logger.error(f"Erro ao mover tarefa de quadrante via menu: {e}", exc_info=True)

def mostrar_menu_contexto(app, point, list_widget):
    try:
        item = list_widget.itemAt(point)
        if not item:
            return

        if not bool(item.flags() & Qt.ItemIsSelectable):
            return

        menu = QMenu(list_widget)

        mover_acao = QAction(get_text("Mover para outro quadrante"), app)
        mover_acao.triggered.connect(lambda: _move_to_quadrant(app, item, list_widget))
        menu.addAction(mover_acao)

        editar_data_acao = QAction(get_text("Editar data/horário"), app)
        editar_data_acao.triggered.connect(lambda: _edit_date_time_dialog(app, item))
        menu.addAction(editar_data_acao)

        menu.addSeparator()

        remover_acao = QAction(get_text("Remover Tarefa"), app)
        remover_acao.triggered.connect(lambda: app.remove_task(item, list_widget))
        menu.addAction(remover_acao)

        menu.exec(list_widget.mapToGlobal(point))

    except Exception as e:
        logger.error(f"Erro ao exibir menu de contexto: {e}", exc_info=True)

def show_context_menu(app, point, list_widget):
    return mostrar_menu_contexto(app, point, list_widget)
