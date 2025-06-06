from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractScrollArea
from PySide6.QtCore import Qt
from gui.models import TrackTableModel
from .keep_toggle_delegate import KeepToggleDelegate

class TrackTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_model = TrackTableModel()
        self.setModel(self.table_model)
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        # ensure the table width matches the column widths
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # match the name column width with the rest
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.setColumnWidth(7, header.defaultSectionSize())
        self.resizeColumnsToContents()
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setItemDelegateForColumn(0, KeepToggleDelegate(self))
        self.setMouseTracking(True)
        # Adjust row spacing whenever the model resets
        self.table_model.modelReset.connect(self._apply_row_spacing)

    def _apply_row_spacing(self):
        """Increase spacing between different track types."""
        vh = self.verticalHeader()
        default = vh.defaultSectionSize()
        prev_type = None
        for row, track in enumerate(self.table_model.get_tracks()):
            height = default
            if prev_type is not None and track.type != prev_type:
                height += 10
            self.setRowHeight(row, height)
            prev_type = track.type

