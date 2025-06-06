
from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from gui.models import TrackTableModel
from .keep_toggle_delegate import KeepToggleDelegate

class TrackTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_model = TrackTableModel()
        self.setModel(self.table_model)
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Fixed)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setItemDelegateForColumn(0, KeepToggleDelegate(self))
        self.setMouseTracking(True)
        # Adjust row spacing whenever the model resets
        self.table_model.modelReset.connect(self._apply_row_spacing)
        # Update column widths whenever the model resets
        self.table_model.modelReset.connect(self.adjust_column_widths)
        # Initial width distribution
        self.adjust_column_widths()

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

    def adjust_column_widths(self):
        """Distribute available width between columns based on average content size."""
        fm = QFontMetrics(self.font())
        cols = self.table_model.columnCount()
        rows = self.table_model.rowCount()
        averages = []
        for c in range(cols):
            total = fm.horizontalAdvance(str(self.table_model.headerData(c, Qt.Horizontal)))
            for r in range(rows):
                idx = self.table_model.index(r, c)
                data = self.table_model.data(idx, Qt.DisplayRole) or ""
                total += fm.horizontalAdvance(str(data))
            averages.append(total / max(rows + 1, 1))
        total_avg = sum(averages)
        if not total_avg:
            return
        width = self.viewport().width()
        for c, avg in enumerate(averages):
            w = int(width * avg / total_avg)
            self.setColumnWidth(c, w)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_column_widths()

