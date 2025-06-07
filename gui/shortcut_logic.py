from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt


class ShortcutLogic:
    def _setup_shortcut_logic(self):
        """Create application shortcuts and connect them to actions."""
        # Navigate between groups
        self.shortcut_next_group = QShortcut(QKeySequence("Ctrl+Tab"), self)
        self.shortcut_next_group.setContext(Qt.ApplicationShortcut)
        self.shortcut_next_group.activated.connect(
            lambda: self._on_next_group(loop=True)
        )
        self.shortcut_prev_group = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        self.shortcut_prev_group.setContext(Qt.ApplicationShortcut)
        self.shortcut_prev_group.activated.connect(
            lambda: self._on_prev_group(loop=True)
        )
        self.shortcut_prev_group_shift = QShortcut(QKeySequence("Shift+Tab"), self)
        self.shortcut_prev_group_shift.setContext(Qt.ApplicationShortcut)
        self.shortcut_prev_group_shift.activated.connect(
            lambda: self._on_prev_group(loop=True)
        )

        # Action bar shortcuts
        if hasattr(self, "action_bar"):
            ab = self.action_bar
            sc = QShortcut(QKeySequence("A"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(ab.btn_def_audio.click)

            sc = QShortcut(QKeySequence("S"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(ab.btn_def_sub.click)

            sc = QShortcut(QKeySequence("F"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(ab.btn_forced.click)

            sc = QShortcut(QKeySequence("W"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(
                lambda: ab.btn_wipe_all.setChecked(not ab.btn_wipe_all.isChecked())
            )

            sc = QShortcut(QKeySequence("P"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(ab.btn_preview.click)

        # Toggle keep/skip on the selected track
        if hasattr(self, "track_table"):
            sc = QShortcut(QKeySequence(Qt.Key_Space), self.track_table)
            sc.setContext(Qt.WidgetWithChildrenShortcut)
            sc.activated.connect(self._toggle_keep_selected)
            self.shortcut_toggle_keep = sc

    def _toggle_keep_selected(self):
        row = self._current_idx()
        if row is None:
            return
        model = self.track_table.table_model
        idx = model.index(row, 0)
        state = model.data(idx, Qt.CheckStateRole)
        new_state = Qt.Unchecked if state == Qt.Checked else Qt.Checked
        model.setData(idx, new_state, Qt.CheckStateRole)
