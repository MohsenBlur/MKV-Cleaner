from PySide6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
)
from PySide6.QtCore import QSettings
from pathlib import Path
import tempfile
import re


def peek_subtitle(fp: Path, tid: int, run_command, extract_cmd, backend, maxlen=15000):
    """Extract and decode subtitle text robustly from an MKV file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".ass", delete=False)
    tmp.close()
    try:
        if backend == "ffmpeg":
            run_command([
                extract_cmd,
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(fp),
                "-map",
                f"0:{tid}",
                tmp.name,
            ], capture=False)
        else:
            run_command([extract_cmd, "tracks", str(fp), f"{tid}:{tmp.name}"], capture=False)
        try:
            out = Path(tmp.name).read_text(encoding="utf-8")[:maxlen]
        except UnicodeDecodeError:
            out = Path(tmp.name).read_text(encoding="latin1")[:maxlen]
    except Exception as e:
        out = f"Could not extract subtitle:\n{e}"
    finally:
        Path(tmp.name).unlink(missing_ok=True)
    return out


def srt_to_html(raw, font_size: int = 13):
    """Convert SRT subtitle text to formatted HTML for preview."""
    raw = raw.lstrip("\ufeffï»¿")
    blocks = re.split(r"\n\s*\n", raw.strip())
    html_blocks = []
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        html = []
        if re.match(r"^\d+$", lines[0]):
            html.append(
                f"<span style='font-weight:bold;color:#fa4;'>{lines[0]}</span><br>"
            )
            lines = lines[1:]
        if lines and re.match(r"^\d{2}:\d{2}:\d{2},\d{3} -->", lines[0]):
            html.append(
                f"<span style='color:#4bc;font-weight:bold'>{lines[0]}</span><br>"
            )
            lines = lines[1:]
        for line in lines:
            line = re.sub(r"^<i>(.*?)</i>$", r"<i>\1</i>", line)
            html.append(f"<span style='color:#fff'>{line}</span>")
        html_blocks.append(
            "<div style='margin-bottom:10px'>" + "".join(html) + "</div>"
        )
    return (
        f"<div style='font-family:Consolas,monospace;font-size:{font_size}px;"
        "background:#20232b;padding:16px 20px;color:#fff;"
        " border-radius:8px;line-height:1.7;'>"
        + "".join(html_blocks)
        + "</div>"
    )


def ass_to_html(raw, font_size: int = 13):
    """Convert ASS/SSA subtitle text to formatted HTML for preview."""
    raw = raw.lstrip("\ufeffï»¿")
    lines = raw.splitlines()
    html = []
    section = None
    small = max(font_size - 2, 8)
    for line in lines:
        lstripped = line.lstrip()
        if lstripped.startswith("[") and lstripped.endswith("]"):
            section = lstripped
            html.append(
                "<div style='margin-top:10px;margin-bottom:2px;'><span style='"
                "font-weight:bold; color:#4bc;'>"
                f"{section}</span></div>"
            )
            continue
        if lstripped.startswith("Format:"):
            small = max(font_size - 2, 8)
            html.append(
                f"<div style='color:#888; font-size:{small}px; margin-bottom:2px;'>"
                f"{lstripped}</div>"
            )
            continue
        if lstripped.startswith("Style:"):
            small = max(font_size - 2, 8)
            html.append(
                f"<div style='color:#aaa; font-size:{small}px; margin-bottom:2px;'>"
                f"{lstripped}</div>"
            )
            continue
        if lstripped.startswith("Dialogue:"):
            parts = lstripped.split(",", 9)
            if len(parts) >= 10:
                start = parts[1]
                end = parts[2]
                actor = parts[4]
                text = parts[9]
                text = re.sub(r"{\\i1}(.*?){\\i0}", r"<i>\1</i>", text)
                text = text.replace(r"\N", "<br>")
                html.append(
                    f"<div style='margin-bottom:10px;'>"
                    f"<span style='font-weight:bold; color:#fa4; font-size:{font_size}px;'>"
                    f"{start}</span> "
                    f"<span style='font-weight:normal; color:#4bc;'>&rarr; {end}</span>"
                    + (
                        f" <span style='color:#888; font-size:{small}px;'>[{actor}]</span>"
                        if actor.strip()
                        else ""
                    )
                    + f"<br><span style='color:#fff;'>{text}</span></div>"
                )
            else:
                html.append(f"<div style='color:#fff'>{lstripped}</div>")
            continue
        if section:
            html.append(f"<div style='color:#aaa; font-size:{small}px;'>{lstripped}</div>")
        else:
            html.append(f"<div style='color:#fff'>{lstripped}</div>")
    return (
        f"<div style='font-family:Consolas,monospace;font-size:{font_size}px;"
        "background:#20232b;padding:16px 20px;color:#fff;"
        " border-radius:8px;line-height:1.7;'>"
        + "".join(html)
        + "</div>"
    )


class SubtitlePreviewWindow(QMainWindow):
    """Popup window for previewing subtitles from multiple files in a group."""

    def __init__(
        self,
        files,
        tid,
        language,
        name,
        run_command,
        extract_cmd,
        backend,
        parent=None,
    ):
        super().__init__(parent)
        self.files = files
        self.tid = tid
        self.language = language
        self.name = name
        self.run_command = run_command
        self.extract_cmd = extract_cmd
        self.backend = backend
        self.settings = QSettings("MKVToolsCorp", "MKVCleaner")
        self.font_size = int(self.settings.value("preview_font_size", 16))
        if self.font_size < 10:
            self.font_size = 10
        self.pos = 0

        self.txt = QTextEdit(readOnly=True)
        nav = QHBoxLayout()
        self.prev = QPushButton("◀ Prev")
        self.nxt = QPushButton("Next ▶")
        nav.addWidget(self.prev)
        nav.addStretch()
        nav.addWidget(self.nxt)
        lay = QVBoxLayout()
        lay.addWidget(self.txt)
        lay.addLayout(nav)
        wrap = QWidget()
        wrap.setLayout(lay)
        self.setCentralWidget(wrap)
        self.resize(900, 500)
        self.prev.clicked.connect(lambda: self.jump(-1))
        self.nxt.clicked.connect(lambda: self.jump(1))
        self.load()

    def load(self):
        fp = self.files[self.pos]
        raw = peek_subtitle(
            fp,
            self.tid,
            self.run_command,
            self.extract_cmd,
            self.backend,
        )
        if "[Events]" in raw and "Dialogue:" in raw:
            self.txt.setHtml(ass_to_html(raw, self.font_size))
        else:
            self.txt.setHtml(srt_to_html(raw, self.font_size))
        self.setWindowTitle(f"{fp.name} — track {self.tid} {self.language} {self.name}")
        self.prev.setEnabled(self.pos > 0)
        self.nxt.setEnabled(self.pos < len(self.files) - 1)

    def jump(self, d):
        newpos = self.pos + d
        if 0 <= newpos < len(self.files):
            self.pos = newpos
            self.load()
