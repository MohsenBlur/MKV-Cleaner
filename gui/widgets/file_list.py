from PySide6.QtWidgets import QListWidget, QListWidgetItem, QListView
from PySide6.QtCore import Qt
import re


class FileList(QListWidget):
    """Simple list widget showing the files in the current group."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Arrange items in multiple columns
        self.setFlow(QListView.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListView.Adjust)
        self.setUniformItemSizes(True)

    def update_files(self, files):
        """Replace the list contents and resize to fit all rows."""
        self.clear()
        for p in files:
            display = re.sub(r"\s*\([^)]*\)", "", p.stem).strip()
            if not display:
                display = p.stem
            item = QListWidgetItem(display)
            # Show full filename in a larger font inside the tooltip
            item.setToolTip(f"<span style='font-size:16px'>{p.name}</span>")
            self.addItem(item)

        self._update_height()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_height()

    def _update_height(self):
        import math

        rows = self.count()
        if rows == 0:
            height = self.sizeHintForRow(0) + 2 * self.frameWidth()
            self.setFixedHeight(height)
            return

        idx = self.model().index(0, 0)
        item_w = self.sizeHintForIndex(idx).width()
        item_h = self.sizeHintForIndex(idx).height()
        cols = max(1, self.viewport().width() // max(1, item_w))
        row_count = math.ceil(rows / cols)
        height = item_h * row_count + 2 * self.frameWidth()
        self.setFixedHeight(height)

