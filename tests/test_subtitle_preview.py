import types
import sys
from pathlib import Path
import tempfile

# Stub PySide6 modules used by gui.subtitle_preview
sys.modules['PySide6'] = types.ModuleType('PySide6')
qtcore = types.ModuleType('PySide6.QtCore')
qtcore.QSettings = object
sys.modules['PySide6.QtCore'] = qtcore
qtwidgets = types.ModuleType('PySide6.QtWidgets')
for cls in (
    'QMainWindow', 'QTextEdit', 'QHBoxLayout', 'QVBoxLayout',
    'QWidget', 'QPushButton'
):
    setattr(qtwidgets, cls, object)
sys.modules['PySide6.QtWidgets'] = qtwidgets

import gui.subtitle_preview as preview


def test_temp_file_removed_on_error(monkeypatch, tmp_path):
    orig_ntf = tempfile.NamedTemporaryFile
    created = []

    def fake_ntf(*args, **kwargs):
        tmp = orig_ntf(*args, dir=tmp_path, **kwargs)
        created.append(Path(tmp.name))
        return tmp

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", fake_ntf)

    def fail_command(*args, **kwargs):
        raise RuntimeError("boom")

    result = preview.peek_subtitle(
        Path("in.mkv"),
        0,
        fail_command,
        "extract",
        "ffmpeg",
    )

    assert "Could not extract subtitle" in result
    assert created and not created[0].exists()
