from PySide6.QtWidgets import QTableView
from gui.models import TrackTableModel

class TrackTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = TrackTableModel()
        self.setModel(self.model)
