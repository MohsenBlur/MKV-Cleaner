import os
import sys
import types

sys.modules['PySide6'] = types.ModuleType('PySide6')
qtwidgets = types.ModuleType('PySide6.QtWidgets')
class DummyDelegate:
    def __init__(self, parent=None):
        pass

    def editorEvent(self, *a, **k):
        return False
qtwidgets.QStyledItemDelegate = DummyDelegate
qtwidgets.QStyle = type('QStyle', (), {})
qtwidgets.QStyleOptionViewItem = type('QStyleOptionViewItem', (), {})
qtwidgets.QApplication = type('QApplication', (), {'style': staticmethod(lambda: None)})
sys.modules['PySide6.QtWidgets'] = qtwidgets

qtcore = types.ModuleType('PySide6.QtCore')
qtcore.QEvent = type('QEvent', (), {'MouseButtonPress': 1, 'MouseMove': 2, 'MouseButtonRelease': 3})
qtcore.Qt = type('Qt', (), {'Checked': 2, 'Unchecked': 0, 'CheckStateRole': 0})
sys.modules['PySide6.QtCore'] = qtcore

qtgui = types.ModuleType('PySide6.QtGui')
class DummyColor:
    def __init__(self, *a, **k):
        pass
qtgui.QColor = DummyColor
sys.modules['PySide6.QtGui'] = qtgui

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.widgets.keep_toggle_delegate import KeepToggleDelegate
from PySide6.QtCore import Qt, QEvent

class DummyModel:
    def __init__(self):
        self.state = Qt.Checked
    def setData(self, idx, value, role):
        self.state = value

class DummyIndex:
    def __init__(self, model):
        self._model = model
    def data(self, role):
        return self._model.state
    def model(self):
        return self._model
    def row(self):
        return 0

class DummyRect:
    def contains(self, pos):
        return True

class DummyOption:
    rect = DummyRect()

class DummyEvent:
    def __init__(self, typ):
        self._typ = typ
    def type(self):
        return self._typ
    def pos(self):
        return 0


def test_reset_drag_clears_state():
    delegate = KeepToggleDelegate()
    model = DummyModel()
    idx = DummyIndex(model)
    opt = DummyOption()

    delegate.editorEvent(DummyEvent(QEvent.MouseButtonPress), model, opt, idx)
    assert delegate._dragging is True
    assert delegate._drag_state == Qt.Unchecked
    delegate.reset_drag()
    assert delegate._dragging is False
    assert delegate._drag_state is None
