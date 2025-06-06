from PySide6.QtWidgets import QListWidget
from PySide6.QtCore import Qt


class FileList(QListWidget):
    """Simple list widget showing the files in the current group."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def update_files(self, files):
        """Replace the list contents and resize to fit all rows."""
        self.clear()
        for p in files:
            self.addItem(str(p.name))

        rows = self.count()
        if rows:
            row_h = self.sizeHintForRow(0)
            height = row_h * rows + 2 * self.frameWidth()
        else:
            height = self.sizeHintForRow(0) + 2 * self.frameWidth()
        self.setFixedHeight(height)

