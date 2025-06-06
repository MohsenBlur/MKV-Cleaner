
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
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Fixed)
        # Hide vertical header that shows row numbers
        self.verticalHeader().setVisible(False)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setItemDelegateForColumn(0, KeepToggleDelegate(self))
        self.setMouseTracking(True)
        # Adjust row spacing whenever the model resets
        self.table_model.modelReset.connect(self._apply_row_spacing)
        # Update column widths whenever the model resets
        self.table_model.modelReset.connect(self.adjust_column_widths)
        # Update height whenever the model resets
        self.table_model.modelReset.connect(self.adjust_table_height)
        # Initial width distribution
        self.adjust_column_widths()
        self.adjust_table_height()

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
        self.adjust_table_height()

    def adjust_column_widths(self):
        """Divide the available width evenly across all columns."""
        cols = self.table_model.columnCount()
        if cols == 0:
            return
        width = self.viewport().width()
        base = width // cols
        for c in range(cols - 1):
            self.setColumnWidth(c, base)
        self.setColumnWidth(cols - 1, width - base * (cols - 1))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_column_widths()

    def adjust_table_height(self):
        """Resize the table so all rows are visible without scrolling."""
        header_h = self.horizontalHeader().height()
        frame = self.frameWidth() * 2
        rows = self.table_model.rowCount()
        total = header_h + frame
        for r in range(rows):
            total += self.rowHeight(r)
        self.setFixedHeight(total)

