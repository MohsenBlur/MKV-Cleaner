# core/tracks.py

from __future__ import annotations
import json
import subprocess
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from core.config import DEFAULTS

logger = logging.getLogger("core.tracks")

@dataclass
class Track:
    idx: int       # index in the UI/table
    tid: int       # real mkvmerge track id
    type: str
    codec: str
    language: str
    forced: bool
    name: str
    default_audio: bool = False
    default_subtitle: bool = False
    removed: bool = False

    def signature(self) -> str:
        return (
            f"{self.tid}-{self.type}-{self.codec}-"
            f"{self.language}-{'F' if self.forced else ''}-{self.name}"
        )

def run_command(cmd: list[str]) -> subprocess.CompletedProcess:
    logger.debug(f"Running: {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        logger.error("Command failed: %s\n%s", exc, exc.stderr)
        raise

def query_tracks(source: Path) -> List[Track]:
    """Query tracks in an MKV file via mkvmerge and return Track objects."""
    result = run_command([DEFAULTS["mkvmerge_cmd"], "-J", str(source)])
    data = json.loads(result.stdout)
    tracks: List[Track] = []
    for i, t in enumerate(data.get("tracks", [])):
        p = t.get("properties", {})
        tracks.append(Track(
            idx=i,
            tid=int(t["id"]),
            type=t.get("type", ""),
            codec=p.get("codec_id", ""),
            language=p.get("language", "und"),
            forced=p.get("forced_track", False),
            name=p.get("track_name", ""),
        ))
    return tracks

def build_cmd(
    source: Path,
    destination: Path,
    tracks: List[Track],
    wipe_forced: bool = False,
    wipe_all: bool = False,
) -> list[str]:
    """Build mkvmerge command for keeping/removing tracks using correct IDs."""
    cmd: list[str] = [DEFAULTS["mkvmerge_cmd"]]

    # Use tid (real mkvmerge track id) everywhere!
    all_audio_ids = [str(t.tid) for t in tracks if t.type == "audio"]
    all_sub_ids   = [str(t.tid) for t in tracks if t.type == "subtitles"]
    kept_audio    = [str(t.tid) for t in tracks if t.type == "audio" and not t.removed]
    kept_sub      = [str(t.tid) for t in tracks if t.type == "subtitles" and not t.removed]

    if kept_audio:
        if set(kept_audio) != set(all_audio_ids):
            cmd += ["--audio-tracks", ",".join(kept_audio)]
    else:
        cmd += ["--no-audio"]

    if wipe_all or not kept_sub:
        cmd += ["--no-subtitles"]
    elif set(kept_sub) != set(all_sub_ids):
        cmd += ["--subtitle-tracks", ",".join(kept_sub)]

    # Forced flags
    if wipe_forced:
        for t in tracks:
            if t.type == "subtitles" and not t.removed:
                cmd += ["--forced-track", f"{t.tid}:no"]
    else:
        for t in tracks:
            if t.type == "subtitles" and t.forced and not t.removed:
                cmd += ["--forced-track", f"{t.tid}:yes"]

    # Default flags
    for t in tracks:
        if not t.removed and t.type == "audio" and t.default_audio:
            cmd += ["--default-track", f"{t.tid}:yes"]
        if not t.removed and t.type == "subtitles" and t.default_subtitle:
            cmd += ["--default-track", f"{t.tid}:yes"]

    # Output and input file MUST come last
    cmd += ["-o", str(destination), str(source)]
    return cmd

def peek_sub(sub_file: Path, max_blocks: int = 5) -> str:
    text = sub_file.read_text(encoding="utf-8", errors="ignore")
    blocks = text.strip().split("\n\n")
    if len(blocks) > max_blocks:
        return "\n\n".join(blocks[:max_blocks]) + "\n\n..."
    return text
