
from PySide6.QtWidgets import (
    QTableView,
    QHeaderView,
    QAbstractScrollArea,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from gui.models import TrackTableModel
from .keep_toggle_delegate import KeepToggleDelegate
from .flag_delegate import FlagDelegate
from .no_focus_delegate import NoFocusDelegate

class TrackTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_model = TrackTableModel()
        self.setModel(self.table_model)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        # Disable built-in grid lines, we'll draw horizontal lines via CSS
        self.setShowGrid(False)
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Fixed)
        # Hide vertical header that shows row numbers
        self.verticalHeader().setVisible(False)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # Prevent flickering scrollbars when resizing
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setItemDelegate(NoFocusDelegate(self))
        self.setItemDelegateForColumn(0, KeepToggleDelegate(self))
        self.setItemDelegateForColumn(5, FlagDelegate(5, self))
        self.setItemDelegateForColumn(6, FlagDelegate(6, self))
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
        self.setToolTip(
            "Select a track here, then use the buttons below to set defaults or remove subtitles."
        )

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
        """Distribute space while keeping certain columns fixed."""
        cols = self.table_model.columnCount()
        if cols == 0:
            return

        header = self.horizontalHeader()

        # Determine widths for ID, Forced and Default columns based on header text
        fixed_cols = [1, 5, 6]
        fixed_widths = {}
        for c in fixed_cols:
            text = self.table_model.headerData(c, Qt.Horizontal, Qt.DisplayRole)
            fm = header.fontMetrics()
            fixed_widths[c] = fm.horizontalAdvance(str(text)) + 20
            self.setColumnWidth(c, fixed_widths[c])

        total_fixed = sum(fixed_widths.values())
        available = self.viewport().width() - total_fixed
        if available < 0:
            available = self.viewport().width()

        remaining_cols = [c for c in range(cols) if c not in fixed_cols]
        if not remaining_cols:
            return
        base = available // len(remaining_cols)
        for c in remaining_cols[:-1]:
            self.setColumnWidth(c, base)
        self.setColumnWidth(remaining_cols[-1], available - base * (len(remaining_cols) - 1))

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

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        delegate = self.itemDelegateForColumn(0)
        if hasattr(delegate, "reset_drag"):
            delegate.reset_drag()

    def leaveEvent(self, event):
        delegate = self.itemDelegateForColumn(0)
        if hasattr(delegate, "reset_drag"):
            delegate.reset_drag()
        super().leaveEvent(event)

