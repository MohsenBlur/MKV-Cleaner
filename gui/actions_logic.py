from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from core.tracks import query_tracks, build_cmd, run_command
from .subtitle_preview import SubtitlePreviewWindow
from .processing import process_files


class ActionsLogic:
    def _setup_action_logic(self):
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_open_files"):
            self.action_bar.btn_open_files.clicked.connect(self.open_files)
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_def_audio"):
            self.action_bar.btn_def_audio.clicked.connect(self.set_default_audio)
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_def_sub"):
            self.action_bar.btn_def_sub.clicked.connect(self.set_default_subtitle)
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_forced"):
            self.action_bar.btn_forced.clicked.connect(self.set_forced_subtitle)
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_wipe_all"):
            self.action_bar.btn_wipe_all.clicked.connect(self.wipe_all_subs)
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_preview"):
            self.action_bar.btn_preview.clicked.connect(self.preview_subtitle)
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_process_group"):
            self.action_bar.btn_process_group.clicked.connect(self.process_group)
        elif hasattr(self, "group_bar") and hasattr(self.group_bar, "btn_process_group"):
            self.group_bar.btn_process_group.clicked.connect(self.process_group)

        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_process_all"):
            self.action_bar.btn_process_all.clicked.connect(self.process_all)
        elif hasattr(self, "group_bar") and hasattr(self.group_bar, "btn_process_all"):
            self.group_bar.btn_process_all.clicked.connect(self.process_all)

    def set_default_audio(self):
        row = self._current_idx()
        if row is None:
            return
        t = self.track_table.table_model.track_at_row(row)
        if t.type != "audio":
            return
        for tr in self.track_table.table_model.get_tracks():
            if tr.type == "audio":
                tr.default_audio = False
        t.default_audio = True
        self.track_table.table_model.update_tracks(self.track_table.table_model.tracks)
        if hasattr(self, "status_bar"):
            msg = f"Default audio set to track {t.tid} ({t.language})"
            if t.name:
                msg += f" - {t.name}"
            self.status_bar.showMessage(msg, 2000)

    def set_default_subtitle(self):
        row = self._current_idx()
        if row is None:
            return
        t = self.track_table.table_model.track_at_row(row)
        if t.type != "subtitles":
            return
        for tr in self.track_table.table_model.get_tracks():
            if tr.type == "subtitles":
                tr.default_subtitle = False
        t.default_subtitle = True
        self.track_table.table_model.update_tracks(self.track_table.table_model.tracks)
        if hasattr(self, "status_bar"):
            msg = f"Default subtitle set to track {t.tid} ({t.language})"
            if t.name:
                msg += f" - {t.name}"
            self.status_bar.showMessage(msg, 2000)

    def set_forced_subtitle(self):
        row = self._current_idx()
        if row is None:
            return
        t = self.track_table.table_model.track_at_row(row)
        if t.type != "subtitles":
            return
        if not t.forced:
            for tr in self.track_table.table_model.get_tracks():
                if tr.type == "subtitles":
                    tr.forced = False
            t.forced = True
            state = "enabled"
        else:
            t.forced = False
            state = "disabled"
        self.track_table.table_model.update_tracks(self.track_table.table_model.tracks)
        if hasattr(self, "status_bar"):
            msg = f"Forced flag {state} on track {t.tid} ({t.language})"
            if t.name:
                msg += f" - {t.name}"
            self.status_bar.showMessage(msg, 2000)

    def wipe_all_subs(self):
        sig = getattr(self, "current_sig", None)
        if sig is None:
            return

        btn = getattr(getattr(self, "action_bar", None), "btn_wipe_all", None)
        wiping = btn.isChecked() if btn is not None else True

        tracks = self.track_table.table_model.get_tracks()
        changed = False

        if wiping:
            self.wipe_sub_state[sig] = [
                t.tid for t in tracks if t.type == "subtitles" and not t.removed
            ]
            for tr in tracks:
                if tr.type == "subtitles" and not tr.removed:
                    tr.removed = True
                    changed = True
            msg = "All subtitles marked for removal"
        else:
            prev = self.wipe_sub_state.get(sig, [])
            for tr in tracks:
                if tr.type == "subtitles" and tr.tid in prev and tr.removed:
                    tr.removed = False
                    changed = True
            msg = "Subtitle selections restored"

        if changed:
            self.track_table.table_model.update_tracks(
                self.track_table.table_model.tracks
            )
            if hasattr(self, "status_bar"):
                self.status_bar.showMessage(msg, 2000)

    def preview_subtitle(self):
        row = self._current_idx()
        if row is None:
            return
        t = self.track_table.table_model.track_at_row(row)
        if t.type != "subtitles":
            return
        files = self.file_groups.get(self.current_sig, [])
        if not files:
            QMessageBox.information(self, "No files", "No files to preview")
            return
        self._preview_win = SubtitlePreviewWindow(
            files,
            t.tid,
            t.language,
            t.name,
            run_command,
            self.app_config.ffmpeg_cmd if self.app_config.backend == "ffmpeg" else self.app_config.mkvextract_cmd,
            self.app_config.backend,
            parent=self,
        )
        self._preview_win.show()

    def process_group(self):
        if not self.current_sig:
            QMessageBox.information(self, "No group", "No group selected")
            return
        files = self.file_groups.get(self.current_sig, [])
        if not files:
            QMessageBox.information(self, "No files", "No files in this group")
            return
        jobs = [(f, self.groups[self.current_sig]) for f in files]
        wipe = self.action_bar.btn_wipe_all.isChecked() or getattr(self, "wipe_all_default", False)
        process_files(
            jobs,
            self.app_config.max_workers,
            lambda src: query_tracks(src, self.app_config),
            lambda s, d, t, wipe_forced=False, wipe_all=False: build_cmd(s, d, t, self.app_config, wipe_forced, wipe_all),
            run_command,
            self.app_config.output_dir,
            wipe,
            parent=self,
        )

    def process_all(self):
        if not self.groups:
            QMessageBox.information(self, "No files", "No files loaded")
            return
        jobs = []
        for sig, files in self.file_groups.items():
            tracks = self.groups[sig]
            for f in files:
                jobs.append((f, tracks))
        wipe = self.action_bar.btn_wipe_all.isChecked() or getattr(self, "wipe_all_default", False)
        process_files(
            jobs,
            self.app_config.max_workers,
            lambda src: query_tracks(src, self.app_config),
            lambda s, d, t, wipe_forced=False, wipe_all=False: build_cmd(s, d, t, self.app_config, wipe_forced, wipe_all),
            run_command,
            self.app_config.output_dir,
            wipe,
            parent=self,
        )
