import os
import sys
import types
from pathlib import Path
import pytest

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

from gui.subtitle_preview import srt_to_html, ass_to_html, peek_subtitle
from gui.theme import COLORS


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
    assert (
        f"<span style='font-weight:bold;color:{COLORS['text_em']};'>1</span><br>" in html
    )
    assert (
        f"<span style='color:{COLORS['text_teal']};font-weight:bold'>00:00:01,000 --> 00:00:04,000</span><br>"
        in html
    )
    assert f"<span style='color:{COLORS['white']}'><i>World</i></span>" in html
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
    assert (
        f"<span style='font-weight:bold; color:{COLORS['text_teal']};'>[Script Info]</span>" in html
    )
    assert (
        f"<div style='color:{COLORS['text_muted']}; font-size:11px;'>Title: Example</div>" in html
    )
    assert "&rarr; 0:00:04.00" in html
    assert "[John]</span>" in html
    assert "<i>World</i><br>Line2" in html


@pytest.mark.parametrize(
    "backend,extract_cmd",
    [
        ("ffmpeg", "ffmpeg"),
        ("mkvtoolnix", "mkvextract"),
    ],
)
def test_peek_subtitle_tmp_removed(monkeypatch, tmp_path, backend, extract_cmd):
    fp = tmp_path / "in.mkv"
    fp.write_text("dummy")

    paths = []

    def fake_run(cmd, capture=False):
        if backend == "ffmpeg":
            out = cmd[-1]
        else:
            out = cmd[3].split(":", 1)[1]
        Path(out).write_text("extracted", encoding="utf-8")
        paths.append(out)

    text = peek_subtitle(fp, 1, fake_run, extract_cmd, backend)

    assert text == "extracted"
    assert paths and not Path(paths[0]).exists()

