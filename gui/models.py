from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from core.tracks import Track
from core.flags import lang_to_flag


class TrackTableModel(QAbstractTableModel):
    def __init__(self, tracks: list[Track] | None = None):
        super().__init__()
        self.tracks: list[Track] = tracks or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.tracks)

    def columnCount(self, parent=QModelIndex()):
        return 8

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() < 0 or index.row() >= len(self.tracks):
            return None
        t = self.tracks[index.row()]

        c = index.column()
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        if role == Qt.CheckStateRole and c == 0:
            return Qt.Checked if not getattr(t, "removed", False) else Qt.Unchecked
        if role == Qt.DisplayRole:
            lang_code = getattr(t, "language", "")
            if t.type in {"audio", "subtitles"}:
                flag = lang_to_flag(lang_code)
                display_lang = f"{flag} {lang_code}" if flag else lang_code
            else:
                display_lang = lang_code
            return {
                1: getattr(t, "tid", ""),
                2: getattr(t, "type", ""),
                3: getattr(t, "codec", ""),
                4: display_lang,
                5: "🚩" if getattr(t, "forced", False) else "",
                6: (
                    "🔊"
                    if getattr(t, "default_audio", False)
                    else ("CC" if getattr(t, "default_subtitle", False) else "")
                ),
                7: getattr(t, "name", ""),
            }.get(c, "")
        return None

    def setData(self, index, value, role=Qt.CheckStateRole):
        if index.isValid() and role == Qt.CheckStateRole and index.column() == 0:
            t = self.tracks[index.row()]
            t.removed = value == Qt.Unchecked
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
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return ["Keep", "ID", "Type", "Codec", "Lang", "Forced", "Default", "Name"][
                    section
                ]
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        return super().headerData(section, orientation, role)

    def update_tracks(self, tracks):
        self.beginResetModel()
        self.tracks = tracks or []
        self.endResetModel()

    def get_tracks(self):
        return self.tracks

    def track_at_row(self, row):
        if 0 <= row < len(self.tracks):
            return self.tracks[row]
        raise IndexError(row)
