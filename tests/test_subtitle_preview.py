import os
import sys
import types

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Stub minimal PySide6 modules required for importing gui.subtitle_preview
sys.modules['PySide6'] = types.ModuleType('PySide6')
qtwidgets = types.ModuleType('PySide6.QtWidgets')
for name in (
    "QMainWindow",
    "QTextEdit",
    "QHBoxLayout",
    "QVBoxLayout",
    "QWidget",
    "QPushButton",
):
    setattr(qtwidgets, name, object)
sys.modules['PySide6.QtWidgets'] = qtwidgets
qtcore = types.ModuleType('PySide6.QtCore')
qtcore.QSettings = object
sys.modules['PySide6.QtCore'] = qtcore

from gui.subtitle_preview import srt_to_html, ass_to_html


def test_srt_to_html_basic():
    raw = (
        "\ufeff1\n"
        "00:00:01,000 --> 00:00:04,000\n"
        "Hello\n"
        "<i>World</i>\n"
        "\n"
        "2\n"
        "00:00:05,000 --> 00:00:06,000\n"
        "Bye"
    )
    html = srt_to_html(raw, font_size=13)
    assert "<span style='font-weight:bold;color:#fa4;'>1</span><br>" in html
    assert (
        "<span style='color:#4bc;font-weight:bold'>00:00:01,000 --> 00:00:04,000</span><br>"
        in html
    )
    assert "<span style='color:#fff'><i>World</i></span>" in html
    assert html.count("margin-bottom:10px") == 2


def test_ass_to_html_basic():
    raw = (
        "[Script Info]\n"
        "Title: Example\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:01.00,0:00:04.00,Default,,0,0,0,,Hello\n"
        "Dialogue: 0,0:00:05.00,0:00:06.00,Default,John,0,0,0,,{\\i1}World{\\i0}\\NLine2"
    )
    html = ass_to_html(raw, font_size=13)
    assert "<span style='font-weight:bold; color:#4bc;'>[Script Info]</span>" in html
    assert "<div style='color:#aaa; font-size:11px;'>Title: Example</div>" in html
    assert "&rarr; 0:00:04.00" in html
    assert "[John]</span>" in html
    assert "<i>World</i><br>Line2" in html
