"""Functions for running file processing jobs with a progress dialog."""

from PySide6.QtCore import QMetaObject, Q_ARG
from PySide6.QtWidgets import QMessageBox
from pathlib import Path
import logging

from .widgets.logo_splash import LogoSplash

logger = logging.getLogger(__name__)
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_files(
    jobs,
    max_workers,
    query_tracks,
    build_cmd,
    run_command,
    output_dir,
    wipe_all_flag,
    parent=None,
):
    """Process multiple files in parallel and report progress/errors in the GUI."""
    if parent is not None:
        parent.setEnabled(False)

    errors = []
    import threading

    lock = threading.Lock()

    def process_one(src, tracks):
        real_tracks = query_tracks(src)
        tid_to_ui = {t.tid: t for t in tracks}
        for t in real_tracks:
            if t.tid in tid_to_ui:
                t_ui = tid_to_ui[t.tid]
                t.removed = t_ui.removed
                t.forced = t_ui.forced
                t.default_audio = t_ui.default_audio
                t.default_subtitle = t_ui.default_subtitle
            else:
                t.removed = False
                t.forced = False
                t.default_audio = False
                t.default_subtitle = False
        # Handle absolute or relative output_dir robustly
        output_dir_path = Path(output_dir)
        dst_dir = (
            output_dir_path
            if output_dir_path.is_absolute()
            else (src.parent / output_dir_path)
        )
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src.name
        cmd = build_cmd(
            src, dst, real_tracks, wipe_forced=False, wipe_all=wipe_all_flag
        )
        logger.info("Running: %s", " ".join(map(str, cmd)))
        try:
            run_command(cmd, capture=False)
        except Exception as e:
            with lock:
                errors.append((str(src), str(e)))
        return src

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_one, src, tracks) for src, tracks in jobs]
        for fut in as_completed(futures):
            fut.result()

    if parent is not None:
        parent.setEnabled(True)

    if errors:
        msg = "\n".join([f"{f}: {err}" for f, err in errors])
        QMessageBox.warning(parent, "Some files failed", msg)
    else:
        QMessageBox.information(parent, "Done", "Processing complete.")
