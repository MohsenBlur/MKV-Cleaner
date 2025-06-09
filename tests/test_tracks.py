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
    defaults.backend = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=True, wipe_all=False)
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

    defaults.backend = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=True, wipe_all=False)
    assert cmd == [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
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
    defaults.backend = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=False, wipe_all=True)
    assert cmd == [
        "mkvmerge",
        "--no-subtitles",
        "--default-track",
        "1:yes",
        "-o",
        str(dst),
        str(src),
    ]

    defaults.backend = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=False, wipe_all=True)
    assert cmd == [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
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
    defaults.backend = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=False, wipe_all=False)
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

    defaults.backend = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=False, wipe_all=False)
    assert cmd == [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
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
    defaults.backend = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=False, wipe_all=False)
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


def test_build_cmd_many_subs_ffmpeg(defaults):
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = []
    for i in range(2):
        tracks.append(
            Track(
                idx=i,
                tid=i,
                type="audio",
                codec="aac",
                language="eng",
                forced=False,
                name=f"A{i}",
                default_audio=True,
            )
        )
    for j in range(10):
        tracks.append(
            Track(
                idx=2 + j,
                tid=2 + j,
                type="subtitles",
                codec="srt",
                language="eng",
                forced=False,
                name=f"S{j}",
                default_subtitle=(j == 9),
                removed=(j != 9),
            )
        )

    defaults.backend = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=False, wipe_all=False)

    expected = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(src),
        "-map",
        "0",
    ]
    for tid in range(2, 11):
        expected += ["-map", f"-0:{tid}"]
    expected += [
        "-disposition:a:0",
        "default",
        "-disposition:a:1",
        "default",
        "-disposition:s:0",
        "default",
        "-c",
        "copy",
        str(dst),
    ]

    assert cmd == expected


def test_build_cmd_wipe_all_keep_one_ffmpeg(defaults):
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = []
    for i in range(2):
        tracks.append(
            Track(
                idx=i,
                tid=i + 1,
                type="audio",
                codec="aac",
                language="eng",
                forced=False,
                name=f"A{i}",
                default_audio=True,
            )
        )
    for j in range(3):
        tracks.append(
            Track(
                idx=2 + j,
                tid=3 + j,
                type="subtitles",
                codec="srt",
                language="eng",
                forced=False,
                name=f"S{j}",
            )
        )
    for t in tracks:
        if t.type == "subtitles":
            t.removed = True
    tracks[3].removed = False

    defaults.backend = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=False, wipe_all=True)

    expected = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(src),
        "-map",
        "0",
        "-map",
        "-0:3",
        "-map",
        "-0:5",
        "-disposition:a:0",
        "default",
        "-disposition:a:1",
        "default",
        "-disposition:s:0",
        "0",
        "-c",
        "copy",
        str(dst),
    ]

    assert cmd == expected


def test_build_cmd_wipe_all_keep_one_mkvmerge(defaults):
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = []
    for i in range(2):
        tracks.append(
            Track(
                idx=i,
                tid=i + 1,
                type="audio",
                codec="aac",
                language="eng",
                forced=False,
                name=f"A{i}",
                default_audio=True,
            )
        )
    for j in range(3):
        tracks.append(
            Track(
                idx=2 + j,
                tid=3 + j,
                type="subtitles",
                codec="srt",
                language="eng",
                forced=False,
                name=f"S{j}",
            )
        )
    for t in tracks:
        if t.type == "subtitles":
            t.removed = True
    tracks[3].removed = False

    defaults.backend = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, defaults, wipe_forced=False, wipe_all=True)

    expected = [
        "mkvmerge",
        "--subtitle-tracks",
        "4",
        "--forced-track",
        "4:no",
        "--default-track",
        "1:yes",
        "--default-track",
        "2:yes",
        "--default-track",
        "4:no",
        "-o",
        str(dst),
        str(src),
    ]

    assert cmd == expected
