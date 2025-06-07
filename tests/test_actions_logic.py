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
    'QWidget', 'QPushButton', 'QLabel', 'LogoSplash', 'QSplashScreen'
):
    setattr(qtwidgets, cls, object)
sys.modules['PySide6.QtWidgets'] = qtwidgets
qtgui = types.ModuleType('PySide6.QtGui')
qtgui.QPixmap = object
sys.modules['PySide6.QtGui'] = qtgui

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
        self.selected = None

    def selectRow(self, row):
        self.selected = row

class DummyButton:
    def __init__(self):
        self._checked = False

    def isChecked(self):
        return self._checked

    def setChecked(self, val):
        self._checked = val

class DummyActionBar:
    def __init__(self):
        self.btn_wipe_all = DummyButton()

class DummyActions(ActionsLogic):
    def __init__(self, tracks, sig="g1"):
        self.track_table = DummyTrackTable(tracks)
        self.status_bar = DummyStatusBar()
        self.action_bar = DummyActionBar()
        self.wipe_sub_state = {}
        self.current_sig = sig
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


def test_selection_preserved_after_actions():
    tracks = [
        Track(idx=0, tid=1, type="subtitles", codec="srt", language="eng", forced=False, name="English"),
        Track(idx=1, tid=2, type="subtitles", codec="srt", language="spa", forced=False, name="Spanish"),
        Track(idx=2, tid=3, type="audio", codec="aac", language="eng", forced=False, name="Audio"),
    ]
    actions = DummyActions(tracks)

    actions.cur_idx = 1
    actions.set_default_subtitle()
    assert actions.track_table.selected == 1

    actions.set_forced_subtitle()
    assert actions.track_table.selected == 1

    actions.cur_idx = 2
    actions.set_default_audio()
    assert actions.track_table.selected == 2

    actions.cur_idx = 1
    actions.action_bar.btn_wipe_all.setChecked(True)
    actions.wipe_all_subs()
    assert actions.track_table.selected == 1


def test_wipe_all_toggle_restores_tracks():
    tracks = [
        Track(idx=0, tid=1, type="subtitles", codec="srt", language="eng", forced=False, name="English"),
        Track(idx=1, tid=2, type="subtitles", codec="srt", language="spa", forced=False, name="Spanish"),
        Track(idx=2, tid=3, type="audio", codec="aac", language="eng", forced=False, name="Audio"),
    ]
    actions = DummyActions(tracks)
    actions.action_bar.btn_wipe_all.setChecked(True)
    actions.wipe_all_subs()
    assert all(t.removed for t in tracks if t.type == "subtitles")

    actions.action_bar.btn_wipe_all.setChecked(False)
    actions.wipe_all_subs()
    assert all(not t.removed for t in tracks if t.type == "subtitles")


def test_wipe_all_state_per_group():
    g1 = [
        Track(idx=0, tid=1, type="subtitles", codec="srt", language="eng", forced=False, name="English"),
    ]
    g2 = [
        Track(idx=0, tid=10, type="subtitles", codec="srt", language="spa", forced=False, name="Spanish"),
    ]

    actions = DummyActions(g1, sig="g1")
    actions.action_bar.btn_wipe_all.setChecked(True)
    actions.wipe_all_subs()
    assert g1[0].removed is True

    actions.current_sig = "g2"
    actions.track_table.table_model.update_tracks(g2)
    actions.action_bar.btn_wipe_all.setChecked(True)
    actions.wipe_all_subs()
    assert g2[0].removed is True

    actions.current_sig = "g1"
    actions.track_table.table_model.update_tracks(g1)
    actions.action_bar.btn_wipe_all.setChecked(False)
    actions.wipe_all_subs()
    assert g1[0].removed is False
    actions.current_sig = "g2"
    actions.track_table.table_model.update_tracks(g2)
    assert g2[0].removed is True
