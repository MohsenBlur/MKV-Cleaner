from typing import Dict, List
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt


class ShortcutLogic:
    """Mixin that defines application keyboard shortcuts."""

    hotkey_map: Dict[str, List[QShortcut]]

    def _append_hotkey_tooltip(self, widget, shortcut: QShortcut) -> None:
        """Add ``Hotkey: <keys>`` line to ``widget`` tooltip."""
        if widget is None:
            return
        tip = widget.toolTip() or ""
        seq = shortcut.key().toString(QKeySequence.NativeText)
        hotkey_line = f"Hotkey: {seq}"
        if hotkey_line in tip:
            return
        if tip and not tip.endswith("\n"):
            tip += "\n"
        tip += hotkey_line
        widget.setToolTip(tip)

    def _register_shortcut(self, name: str, shortcut: QShortcut, widget=None) -> None:
        self.hotkey_map.setdefault(name, []).append(shortcut)
        if widget is not None:
            self._append_hotkey_tooltip(widget, shortcut)

    def _setup_shortcut_logic(self):
        """Create application shortcuts and connect them to actions."""
        self.hotkey_map = {}

        # Navigate between groups
        sc = QShortcut(QKeySequence("Ctrl+Tab"), self)
        sc.setContext(Qt.ApplicationShortcut)
        sc.activated.connect(lambda: self._on_next_group(loop=True))
        self._register_shortcut("Next group", sc)

        sc = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        sc.setContext(Qt.ApplicationShortcut)
        sc.activated.connect(lambda: self._on_prev_group(loop=True))
        self._register_shortcut("Previous group", sc)

        sc = QShortcut(QKeySequence("Shift+Tab"), self)
        sc.setContext(Qt.ApplicationShortcut)
        sc.activated.connect(lambda: self._on_prev_group(loop=True))
        self._register_shortcut("Previous group", sc)

        sc = QShortcut(QKeySequence(Qt.Key_Right), self)
        sc.setContext(Qt.ApplicationShortcut)
        sc.activated.connect(self._on_next_group)
        self._register_shortcut("Next group", sc)

        sc = QShortcut(QKeySequence(Qt.Key_Left), self)
        sc.setContext(Qt.ApplicationShortcut)
        sc.activated.connect(self._on_prev_group)
        self._register_shortcut("Previous group", sc)

        # Action bar shortcuts
        if hasattr(self, "action_bar"):
            ab = self.action_bar

            sc = QShortcut(QKeySequence("A"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(ab.btn_def_audio.click)
            self._register_shortcut("Default audio", sc, ab.btn_def_audio)

            sc = QShortcut(QKeySequence("S"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(ab.btn_def_sub.click)
            self._register_shortcut("Default subtitle", sc, ab.btn_def_sub)

            sc = QShortcut(QKeySequence("F"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(ab.btn_forced.click)
            self._register_shortcut("Set forced", sc, ab.btn_forced)

            sc = QShortcut(QKeySequence("W"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(lambda: ab.btn_wipe_all.isEnabled() and ab.btn_wipe_all.click())
            self._register_shortcut("Wipe all subtitles", sc, ab.btn_wipe_all)

            sc = QShortcut(QKeySequence("O"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(lambda: ab.btn_open_files.isEnabled() and ab.btn_open_files.click())
            self._register_shortcut("Open files", sc, ab.btn_open_files)

            sc = QShortcut(QKeySequence("Ctrl+O"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(lambda: ab.btn_open_files.isEnabled() and ab.btn_open_files.click())
            self._register_shortcut("Open files", sc, ab.btn_open_files)

            if hasattr(self.group_bar, "btn_process_group"):
                sc = QShortcut(QKeySequence("Ctrl+G"), self)
                sc.setContext(Qt.ApplicationShortcut)
                sc.activated.connect(lambda: self.group_bar.btn_process_group.isEnabled() and self.group_bar.btn_process_group.click())
                self._register_shortcut("Process group", sc, self.group_bar.btn_process_group)

            if hasattr(self.group_bar, "btn_process_all"):
                sc = QShortcut(QKeySequence("Ctrl+Return"), self)
                sc.setContext(Qt.ApplicationShortcut)
                sc.activated.connect(lambda: self.group_bar.btn_process_all.isEnabled() and self.group_bar.btn_process_all.click())
                self._register_shortcut("Process all", sc, self.group_bar.btn_process_all)

            sc = QShortcut(QKeySequence(Qt.Key_Escape), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(self._open_preferences)
            # preferences button is on group bar
            if hasattr(self, "group_bar"):
                self._register_shortcut("Preferences", sc, self.group_bar.btn_prefs)
            else:
                self._register_shortcut("Preferences", sc)

            sc = QShortcut(QKeySequence("P"), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(ab.btn_preview.click)
            self._register_shortcut("Preview subtitle", sc, ab.btn_preview)

        # Number keys for selecting groups
        if hasattr(self, "group_bar"):
            for i in range(1, 10):
                sc = QShortcut(QKeySequence(str(i)), self)
                sc.setContext(Qt.ApplicationShortcut)
                sc.activated.connect(lambda i=i: self._activate_group_index(i - 1))
                self._register_shortcut(f"Select group {i}", sc)

        # Toggle keep/skip on the selected track
        if hasattr(self, "track_table"):
            sc = QShortcut(QKeySequence(Qt.Key_Space), self.track_table)
            sc.setContext(Qt.WidgetWithChildrenShortcut)
            sc.activated.connect(self._toggle_keep_selected)
            self.shortcut_toggle_keep = sc
            self._register_shortcut("Toggle keep track", sc)

            sc = QShortcut(QKeySequence(Qt.Key_Up), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(self._on_prev_track)
            self._register_shortcut("Previous track", sc)

            sc = QShortcut(QKeySequence(Qt.Key_Down), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(self._on_next_track)
            self._register_shortcut("Next track", sc)

            sc = QShortcut(QKeySequence(Qt.Key_Backspace), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(self._empty_current_group)
            self._register_shortcut("Empty group", sc)

            sc = QShortcut(QKeySequence(Qt.Key_Delete), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(self._empty_current_group)
            self._register_shortcut("Empty group", sc)

    def _toggle_keep_selected(self):
        row = self._current_idx()
        if row is None:
            return
        model = self.track_table.table_model
        idx = model.index(row, 0)
        state = model.data(idx, Qt.CheckStateRole)
        new_state = Qt.Unchecked if state == Qt.Checked else Qt.Checked
        model.setData(idx, new_state, Qt.CheckStateRole)

    def _activate_group_index(self, idx: int) -> None:
        if not hasattr(self, "group_bar"):
            return
        btn = self.group_bar.button_at(idx)
        if btn and btn.isEnabled():
            btn.click()

    def _on_prev_track(self) -> None:
        if not hasattr(self, "track_table"):
            return
        row = self._current_idx()
        model = self.track_table.table_model
        count = model.rowCount()
        if count == 0:
            return
        if row is None:
            self.track_table.selectRow(0)
        elif row > 0:
            self.track_table.selectRow(row - 1)

    def _on_next_track(self) -> None:
        if not hasattr(self, "track_table"):
            return
        row = self._current_idx()
        model = self.track_table.table_model
        count = model.rowCount()
        if count == 0:
            return
        if row is None:
            self.track_table.selectRow(0)
        elif row < count - 1:
            self.track_table.selectRow(row + 1)
