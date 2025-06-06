from pathlib import Path
import copy
from core.tracks import query_tracks


class GroupLogic:
    def _setup_group_logic(self):
        self.groups = {}  # {sig: [Track]}
        self.file_groups = {}  # {sig: [Path]}
        self.current_sig = None
        if hasattr(self, "file_list"):
            self.file_list.clear()
        if hasattr(self, "group_bar") and hasattr(self.group_bar, "prevClicked"):
            self.group_bar.prevClicked.connect(self._on_prev_group)
            self.group_bar.nextClicked.connect(self._on_next_group)
            self.group_bar.update_nav_buttons(None)
            self._update_process_buttons()

    def _on_group_button_clicked(self, btn):
        idx = None
        for i, (_, b) in enumerate(self.group_bar.group_buttons):
            if b is btn:
                idx = i
                break
        if idx is not None:
            self._on_group_change_idx(idx)

    def _on_group_change_idx(self, idx):
        sig = self.group_bar.sig_at(idx)
        if sig is None:
            self.current_sig = None
            self.track_table.table_model.update_tracks([])
            if hasattr(self, "file_list"):
                self.file_list.update_files([])
            return

        self.current_sig = sig
        self.track_table.table_model.update_tracks(self.groups[sig])
        if hasattr(self, "file_list"):
            self.file_list.update_files(self.file_groups.get(sig, []))

        self.group_bar.update_nav_buttons(idx)
        self._update_process_buttons()

    def add_files_to_groups(self, paths):
        for p in paths:
            tracks = query_tracks(Path(p), self.app_config)
            sig = ";".join(t.signature() for t in tracks)
            if sig not in self.groups:
                self.groups[sig] = [copy.deepcopy(t) for t in tracks]
                self.file_groups[sig] = []
                tooltip = str(Path(p).name)
                btn = self.group_bar.add_group_button(sig, tooltip=tooltip)
                btn.clicked.connect(
                    lambda checked, b=btn: self._on_group_button_clicked(b)
                )
            self.file_groups[sig].append(Path(p))
            filestr = "\n".join(str(x.name) for x in self.file_groups[sig])
            self.group_bar.update_button_tooltip(sig, filestr)
            if sig == self.current_sig and hasattr(self, "file_list"):
                self.file_list.update_files(self.file_groups[sig])
        if self.group_bar.group_buttons:
            if self.current_sig is None:
                self.group_bar.set_checked(0)
                self._on_group_change_idx(0)
            else:
                idx = self._current_group_idx()
                self.group_bar.update_nav_buttons(idx)
        self._update_process_buttons()

    def _reload_all_groups(self):
        """Re-import already loaded files using the current backend."""
        all_paths = []
        for files in self.file_groups.values():
            all_paths.extend(files)

        self.groups.clear()
        self.file_groups.clear()
        self.current_sig = None
        self.group_bar.clear()
        self.track_table.table_model.update_tracks([])
        if hasattr(self, "file_list"):
            self.file_list.update_files([])
        self._update_process_buttons()

        if all_paths:
            self.add_files_to_groups(all_paths)

    def _current_group_idx(self):
        for i, (sig, _) in enumerate(self.group_bar.group_buttons):
            if sig == self.current_sig:
                return i
        return None

    def _on_prev_group(self, loop: bool = False):
        idx = self._current_group_idx()
        if idx is None:
            return
        if idx <= 0:
            if not loop:
                return
            idx = len(self.group_bar.group_buttons) - 1
        else:
            idx -= 1
        self.group_bar.set_checked(idx)
        self._on_group_change_idx(idx)

    def _on_next_group(self, loop: bool = False):
        idx = self._current_group_idx()
        if idx is None:
            return
        if idx >= len(self.group_bar.group_buttons) - 1:
            if not loop:
                return
            idx = 0
        else:
            idx += 1
        self.group_bar.set_checked(idx)
        self._on_group_change_idx(idx)

    def _update_process_buttons(self):
        if not hasattr(self, "group_bar"):
            return
        if hasattr(self.group_bar, "btn_process_group"):
            files = self.file_groups.get(self.current_sig, [])
            self.group_bar.btn_process_group.setEnabled(bool(files))
        if hasattr(self.group_bar, "btn_process_all"):
            has_files = any(self.file_groups.values())
            self.group_bar.btn_process_all.setEnabled(has_files)
