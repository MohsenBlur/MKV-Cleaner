from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.tracks import build_cmd, Track  # noqa: E402


def test_build_cmd_flags(defaults):
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = [
        Track(
            idx=0,
            tid=1,
            type="audio",
            codec="aac",
            language="eng",
            forced=False,
            name="English",
            default_audio=True,
        ),
        Track(
            idx=1,
            tid=2,
            type="subtitles",
            codec="srt",
            language="eng",
            forced=True,
            name="English CC",
            default_subtitle=True,
        ),
    ]
    defaults["backend"] = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, wipe_forced=True, wipe_all=False)
    assert cmd == [
        "mkvmerge",
        "--forced-track",
        "2:no",
        "--default-track",
        "1:yes",
        "--default-track",
        "2:yes",
        "-o",
        str(dst),
        str(src),
    ]

    defaults["backend"] = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, wipe_forced=True, wipe_all=False)
    assert cmd == [
        "ffmpeg",
        "-i",
        str(src),
        "-map",
        "0",
        "-disposition:a:0",
        "default",
        "-disposition:s:0",
        "default",
        "-c",
        "copy",
        str(dst),
    ]


def test_build_cmd_wipe_all(defaults):
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = [
        Track(
            idx=0,
            tid=1,
            type="audio",
            codec="aac",
            language="eng",
            forced=False,
            name="English",
            default_audio=True,
        ),
        Track(
            idx=1,
            tid=2,
            type="subtitles",
            codec="srt",
            language="eng",
            forced=True,
            name="English CC",
            default_subtitle=True,
        ),
    ]
    defaults["backend"] = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=True)
    assert cmd == [
        "mkvmerge",
        "--no-subtitles",
        "--forced-track",
        "2:yes",
        "--default-track",
        "1:yes",
        "--default-track",
        "2:yes",
        "-o",
        str(dst),
        str(src),
    ]

    defaults["backend"] = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=True)
    assert cmd == [
        "ffmpeg",
        "-i",
        str(src),
        "-map",
        "0",
        "-map",
        "-0:2",
        "-disposition:a:0",
        "default",
        "-c",
        "copy",
        str(dst),
    ]


def test_build_cmd_forced_default_ffmpeg(defaults):
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = [
        Track(
            idx=0,
            tid=1,
            type="audio",
            codec="aac",
            language="eng",
            forced=False,
            name="English",
            default_audio=True,
        ),
        Track(
            idx=1,
            tid=2,
            type="subtitles",
            codec="srt",
            language="eng",
            forced=True,
            name="English CC",
            default_subtitle=True,
        ),
    ]
    defaults["backend"] = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=False)
    assert cmd == [
        "mkvmerge",
        "--forced-track",
        "2:yes",
        "--default-track",
        "1:yes",
        "--default-track",
        "2:yes",
        "-o",
        str(dst),
        str(src),
    ]

    defaults["backend"] = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=False)
    assert cmd == [
        "ffmpeg",
        "-i",
        str(src),
        "-map",
        "0",
        "-disposition:a:0",
        "default",
        "-disposition:s:0",
        "forced+default",
        "-c",
        "copy",
        str(dst),
    ]
def test_build_cmd_full_flags(defaults):
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = [
        Track(
            idx=0,
            tid=1,
            type="audio",
            codec="aac",
            language="eng",
            forced=False,
            name="English",
            default_audio=False,
        ),
        Track(
            idx=1,
            tid=2,
            type="audio",
            codec="aac",
            language="deu",
            forced=False,
            name="Deutsch",
            default_audio=True,
        ),
        Track(
            idx=2,
            tid=3,
            type="subtitles",
            codec="srt",
            language="eng",
            forced=False,
            name="English Subs",
            default_subtitle=False,
        ),
        Track(
            idx=3,
            tid=4,
            type="subtitles",
            codec="srt",
            language="spa",
            forced=True,
            name="Spanish",
            default_subtitle=True,
        ),
    ]
    defaults["backend"] = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=False)
    assert cmd == [
        "mkvmerge",
        "--forced-track",
        "3:no",
        "--forced-track",
        "4:yes",
        "--default-track",
        "1:no",
        "--default-track",
        "2:yes",
        "--default-track",
        "3:no",
        "--default-track",
        "4:yes",
        "-o",
        str(dst),
        str(src),
    ]
