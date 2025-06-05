import types
import sys

sys.modules['PySide6'] = types.ModuleType('PySide6')
qtcore = types.ModuleType('PySide6.QtCore')
qtcore.Qt = type('Qt', (), {
    'Checked': 2,
    'Unchecked': 0,
    'CheckStateRole': 0,
    'DisplayRole': 1,
    'ItemIsEnabled': 1,
    'ItemIsSelectable': 2,
    'ItemIsUserCheckable': 4
})
qtcore.QAbstractTableModel = object
qtcore.QModelIndex = object
sys.modules['PySide6.QtCore'] = qtcore
from PySide6.QtCore import Qt

from gui.models import TrackTableModel
from core.tracks import Track


def test_track_table_model_basic():
    tracks = [
        Track(idx=0, tid=1, type="audio", codec="aac", language="eng", forced=False, name="English")
    ]
    model = TrackTableModel(tracks)
    # Fake the Qt signal used in setData
    model.dataChanged = type('sig', (), {'emit': lambda *a, **k: None})()
    assert model.rowCount() == 1

    class DummyIndex:
        def __init__(self, row, column):
            self._r = row
            self._c = column
        def row(self):
            return self._r
        def column(self):
            return self._c
        def isValid(self):
            return 0 <= self._r and 0 <= self._c

    idx = DummyIndex(0, 0)
    assert model.data(idx, role=Qt.CheckStateRole) == Qt.Checked
    model.setData(idx, Qt.Unchecked, Qt.CheckStateRole)
    assert tracks[0].removed is True
    assert model.data(idx, role=Qt.CheckStateRole) == Qt.Unchecked
    assert model.track_at_row(0) is tracks[0]


    try:
        model.track_at_row(1)
    except IndexError:
        pass
    else:
        assert False, "expected IndexError"

