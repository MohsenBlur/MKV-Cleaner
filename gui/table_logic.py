from PySide6.QtCore import Qt

class TableLogic:
    def _setup_table_logic(self):
        self.track_table.clicked.connect(self._on_table_clicked)
        self.track_table.selectionModel().currentChanged.connect(
            self._on_selection_change
        )
        self.track_table.table_model.modelReset.connect(
            lambda: self._on_selection_change(self.track_table.currentIndex(), None)
        )
        self.track_table.doubleClicked.connect(self._on_table_double_clicked)
        self._on_selection_change(self.track_table.currentIndex(), None)

    def _on_table_clicked(self, index):
        if index.column() == 0:
            # Delegate handles toggling, just refresh selection state
            self.track_table.table_model.dataChanged.emit(index, index, [Qt.CheckStateRole])
        self._on_selection_change(self.track_table.currentIndex(), None)

    def _on_selection_change(self, current, _):
        ab = self.action_bar
        for btn in (
            ab.btn_def_audio,
            ab.btn_def_sub,
            ab.btn_forced,
            ab.btn_wipe_all,
            ab.btn_preview,
        ):
            btn.setEnabled(False)

        # Enable wipe all when a group is active and has subtitle tracks
        sig = getattr(self, "current_sig", None)
        if sig is not None:
            tracks = getattr(self, "groups", {}).get(sig, [])
            if any(t.type == "subtitles" for t in tracks):
                ab.btn_wipe_all.setEnabled(True)

        if not current.isValid():
            return

        t = self.track_table.table_model.track_at_row(current.row())
        if t.removed:
            if t.type == "subtitles":
                ab.btn_wipe_all.setEnabled(True)
            return

        if t.type == "audio":
            ab.btn_def_audio.setEnabled(True)
        elif t.type == "subtitles":
            ab.btn_def_sub.setEnabled(True)
            ab.btn_forced.setEnabled(True)
            ab.btn_wipe_all.setEnabled(True)
            ab.btn_preview.setEnabled(True)

    def _current_idx(self):
        ci = self.track_table.currentIndex()
        return None if not ci.isValid() else ci.row()

    def _on_table_double_clicked(self, index):
        if not index.isValid():
            return
        t = self.track_table.table_model.track_at_row(index.row())
        if t.type == "subtitles" and self.action_bar.btn_preview.isEnabled():
            self.preview_subtitle()
