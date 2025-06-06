from PySide6.QtWidgets import QTableView
from PySide6.QtCore import Qt
from gui.models import TrackTableModel
from .keep_toggle_delegate import KeepToggleDelegate

class TrackTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_model = TrackTableModel()
        self.setModel(self.table_model)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.setItemDelegateForColumn(0, KeepToggleDelegate(self))
        self.setMouseTracking(True)

