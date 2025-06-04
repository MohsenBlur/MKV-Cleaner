from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any

class TrackTableModel(QAbstractTableModel):
    def __init__(self, tracks=None):
        super().__init__()
        self.tracks = tracks or []

    def rowCount(self, parent=QModelIndex()):
        if isinstance(self.tracks, dict):
            return len(self.tracks)
        return len(self.tracks)

    def columnCount(self, parent=QModelIndex()):
        return 8

    def data(self, index, role=Qt.DisplayRole):
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
            return Qt.Checked if not getattr(t, 'removed', False) else Qt.Unchecked
        if role == Qt.DisplayRole:
            return {
                1: getattr(t, 'tid', ''),
                2: getattr(t, 'type', ''),
                3: getattr(t, 'codec', ''),
                4: getattr(t, 'language', ''),
                5: "🚩" if getattr(t, 'forced', False) else "",
                6: "🔊" if getattr(t, 'default_audio', False) else ("CC" if getattr(t, 'default_subtitle', False) else ""),
                7: getattr(t, 'name', ''),
            }.get(c, "")
        return None

    def setData(self, index, value, role=Qt.CheckStateRole):
        if index.isValid() and role == Qt.CheckStateRole and index.column() == 0:
            if isinstance(self.tracks, dict):
                keys = sorted(self.tracks.keys())
                t = self.tracks[keys[index.row()]]
            else:
                t = self.tracks[index.row()]
            t.removed = (value == Qt.Unchecked)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        base = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 0:
            return base | Qt.ItemIsUserCheckable
        return base

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Keep", "ID", "Type", "Codec", "Lang", "Forced", "Default", "Name"][section]
        return super().headerData(section, orientation, role)

    def update_tracks(self, tracks):
        self.beginResetModel()
        self.tracks = tracks or []
        self.endResetModel()

    def get_tracks(self):
        return self.tracks
