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
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_process_all"):
            self.action_bar.btn_process_all.clicked.connect(self.process_all)

    def set_default_audio(self):
        print("Default Audio button clicked")

    def set_default_subtitle(self):
        print("Default Subtitle button clicked")

    def set_forced_subtitle(self):
        print("Set Forced Subtitle button clicked")

    def wipe_all_subs(self):
        print("Wipe All Subs button clicked")

    def preview_subtitle(self):
        print("Preview Subtitle button clicked")

    def process_group(self):
        print("Process Group button clicked")

    def process_all(self):
        print("Process All button clicked")
