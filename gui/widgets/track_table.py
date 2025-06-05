"""Widget wrapping ``QTableView`` configured with :class:`TrackTableModel`."""

from PySide6.QtWidgets import QTableView, QWidget
from gui.models import TrackTableModel


class TrackTable(QTableView):
    """Table view specialized for showing and editing track lists."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model = TrackTableModel()
        self.setModel(self.model)
