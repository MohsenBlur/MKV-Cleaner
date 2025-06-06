from pathlib import Path
import copy
from core.tracks import query_tracks


class GroupLogic:
    def _setup_group_logic(self):
        self.groups = {}  # {sig: [Track]}
        self.file_groups = {}  # {sig: [Path]}
        self.current_sig = None


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
            return
        self.current_sig = sig
        self.track_table.table_model.update_tracks(self.groups[sig])

    def add_files_to_groups(self, paths):
        for p in paths:
            tracks = query_tracks(Path(p))
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
        if self.group_bar.group_buttons:
            self.group_bar.set_checked(0)
            self._on_group_change_idx(0)

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

        if all_paths:
            self.add_files_to_groups(all_paths)
