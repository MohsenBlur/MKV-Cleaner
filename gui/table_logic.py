"""Logic for interaction with the track table widget."""

from PySide6.QtCore import Qt, QModelIndex


class TableLogic:
    """Mixin dealing with selections and state changes in the track table."""

    def _setup_table_logic(self) -> None:
        self.track_table.clicked.connect(self._on_table_clicked)
        self.track_table.selectionModel().currentChanged.connect(self._on_selection_change)

    def _on_table_clicked(self, index: QModelIndex) -> None:
        if index.column() == 0:
            t = self.track_table.model.track_at_row(index.row())
            t.removed = not t.removed
            self.track_table.model.dataChanged.emit(index, index, [Qt.CheckStateRole])
        self._on_selection_change(self.track_table.currentIndex(), None)

    def _on_selection_change(self, current: QModelIndex, _: QModelIndex) -> None:
        for btn in (
            self.action_bar.btn_def_audio, self.action_bar.btn_def_sub, self.action_bar.btn_forced,
            self.action_bar.btn_wipe_all, self.action_bar.btn_preview
        ):
            btn.setEnabled(False)
        if not current.isValid():
            return
        t = self.track_table.model.track_at_row(current.row())
        if t.removed:
            self.action_bar.btn_wipe_all.setEnabled(t.type == "subtitles")
            return
        if t.type == "audio":
            self.action_bar.btn_def_audio.setEnabled(True)
        elif t.type == "subtitles":
            self.action_bar.btn_def_sub.setEnabled(True)
            self.action_bar.btn_forced.setEnabled(True)
            self.action_bar.btn_wipe_all.setEnabled(True)
            self.action_bar.btn_preview.setEnabled(True)

    def _current_idx(self) -> int | None:
        ci = self.track_table.currentIndex()
        return None if not ci.isValid() else ci.row()
