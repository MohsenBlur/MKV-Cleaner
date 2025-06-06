from PySide6.QtWidgets import QTableView
from gui.models import TrackTableModel
from .keep_toggle_delegate import KeepToggleDelegate

class TrackTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = TrackTableModel()
        self.setModel(self.model)
        self.setItemDelegateForColumn(0, KeepToggleDelegate(self))
