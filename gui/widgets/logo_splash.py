from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen
from pathlib import Path


class LogoSplash(QSplashScreen):
    """Simple splash screen showing the application logo."""

    def __init__(self, parent=None):
        # Resolve the application root directory to load the logo image
        # correctly regardless of the execution context. ``__file__`` lives
        # under ``gui/widgets`` so ``parents[2]`` points to the repository
        # root where ``MKV-Cleaner_logo.png`` is located.
        pixmap_path = Path(__file__).resolve().parents[2] / "MKV-Cleaner_logo.png"
        pixmap = QPixmap(str(pixmap_path))
        pixmap = pixmap.scaled(
            pixmap.width() // 2,
            pixmap.height() // 2,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        if parent is not None:
            max_size = parent.size()
            if pixmap.width() > max_size.width() or pixmap.height() > max_size.height():
                pixmap = pixmap.scaled(max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().__init__(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        if parent is not None:
            center = parent.geometry().center()
            self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)
        self._canceled = False

    def setValue(self, val):
        pass  # kept for API compatibility

    def wasCanceled(self):
        return False
