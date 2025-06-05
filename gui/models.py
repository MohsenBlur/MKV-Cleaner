"""Qt table model for displaying and editing track information."""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import Any, Iterable


class TrackTableModel(QAbstractTableModel):
    """Model storing :class:`core.tracks.Track` objects for ``QTableView``."""

    def __init__(self, tracks: Iterable[Any] | None = None) -> None:
        super().__init__()
        self.tracks = tracks or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if isinstance(self.tracks, dict):
            return len(self.tracks)
        return len(self.tracks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 8

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if isinstance(self.tracks, dict):
            keys = sorted(self.tracks.keys())
            if index.row() < 0 or index.row() >= len(keys):
                return None
            key = keys[index.row()]
            t = self.tracks[key]
        else:
            if index.row() < 0 or index.row() >= len(self.tracks):
                return None
            t = self.tracks[index.row()]

        c = index.column()
        if role == Qt.CheckStateRole and c == 0:
            return Qt.Checked if not getattr(t, "removed", False) else Qt.Unchecked
        if role == Qt.DisplayRole:
            return {
                1: getattr(t, "tid", ""),
                2: getattr(t, "type", ""),
                3: getattr(t, "codec", ""),
                4: getattr(t, "language", ""),
                5: "🚩" if getattr(t, "forced", False) else "",
                6: (
                    "🔊"
                    if getattr(t, "default_audio", False)
                    else ("CC" if getattr(t, "default_subtitle", False) else "")
                ),
                7: getattr(t, "name", ""),
            }.get(c, "")
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.CheckStateRole) -> bool:
        if index.isValid() and role == Qt.CheckStateRole and index.column() == 0:
            if isinstance(self.tracks, dict):
                keys = sorted(self.tracks.keys())
                t = self.tracks[keys[index.row()]]
            else:
                t = self.tracks[index.row()]
            t.removed = value == Qt.Unchecked
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        base = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 0:
            return base | Qt.ItemIsUserCheckable
        return base

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Keep", "ID", "Type", "Codec", "Lang", "Forced", "Default", "Name"][
                section
            ]
        return super().headerData(section, orientation, role)

    def update_tracks(self, tracks: Iterable[Any] | None) -> None:
        self.beginResetModel()
        self.tracks = tracks or []
        self.endResetModel()

    def get_tracks(self) -> Iterable[Any] | None:
        return self.tracks

    def track_at_row(self, row: int) -> Any:
        if isinstance(self.tracks, dict):
            keys = sorted(self.tracks.keys())
            if 0 <= row < len(keys):
                return self.tracks[keys[row]]
            raise KeyError(row)
        else:
            if 0 <= row < len(self.tracks):
                return self.tracks[row]
            raise IndexError(row)
