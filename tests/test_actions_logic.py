import types
import sys

# Stub PySide6 modules
sys.modules['PySide6'] = types.ModuleType('PySide6')
qtcore = types.ModuleType('PySide6.QtCore')
qtcore.Qt = type('Qt', (), {'WindowModal': 0, 'QueuedConnection': 0})
qtcore.QMetaObject = type('QMetaObject', (), {'invokeMethod': lambda *a, **k: None})
qtcore.Q_ARG = lambda typ, val: val
qtcore.QSettings = object
sys.modules['PySide6.QtCore'] = qtcore
qtwidgets = types.ModuleType('PySide6.QtWidgets')
qtwidgets.QMessageBox = type('QMessageBox', (), {
    'warning': staticmethod(lambda *a, **k: None),
    'information': staticmethod(lambda *a, **k: None),
})
# Additional classes used by subtitle_preview imports
for cls in (
    'QMainWindow', 'QTextEdit', 'QHBoxLayout', 'QVBoxLayout',
    'QWidget', 'QPushButton', 'QProgressDialog'
):
    setattr(qtwidgets, cls, object)
sys.modules['PySide6.QtWidgets'] = qtwidgets

from gui.actions_logic import ActionsLogic
from core.tracks import Track

class DummyStatusBar:
    def __init__(self):
        self.msgs = []
    def showMessage(self, msg, timeout):
        self.msgs.append((msg, timeout))

class DummyModel:
    def __init__(self, tracks):
        self.tracks = tracks
    def get_tracks(self):
        return self.tracks
    def update_tracks(self, tracks):
        self.tracks = tracks
    def track_at_row(self, row):
        return self.tracks[row]

class DummyTrackTable:
    def __init__(self, tracks):
        self.table_model = DummyModel(tracks)

class DummyActions(ActionsLogic):
    def __init__(self, tracks):
        self.track_table = DummyTrackTable(tracks)
        self.status_bar = DummyStatusBar()
        self.cur_idx = 0
    def _current_idx(self):
        return self.cur_idx


def test_only_one_forced_subtitle():
    tracks = [
        Track(idx=0, tid=1, type="subtitles", codec="srt", language="eng", forced=False, name="English"),
        Track(idx=1, tid=2, type="subtitles", codec="srt", language="spa", forced=False, name="Spanish"),
    ]
    actions = DummyActions(tracks)
    actions.set_forced_subtitle()
    assert tracks[0].forced is True
    assert tracks[1].forced is False

    actions.cur_idx = 1
    actions.set_forced_subtitle()
    assert tracks[0].forced is False
    assert tracks[1].forced is True

    actions.set_forced_subtitle()
    assert tracks[0].forced is False
    assert tracks[1].forced is False
