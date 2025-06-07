"""Delegate drawing a toggle button for keeping or removing a track."""

from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem, QApplication
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QEvent


class KeepToggleDelegate(QStyledItemDelegate):
    """Delegate that paints a button-like toggle for keeping/removing tracks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.checked_color = QColor("#3584e4")
        self.unchecked_color = QColor("#2a2c34")
        self.hover_color = QColor("#51a4fc")

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        # Remove focus state so no cell highlight outline is drawn
        opt.state &= ~QStyle.State_HasFocus

        painter.save()
        track = None
        if hasattr(index.model(), "track_at_row"):
            try:
                track = index.model().track_at_row(index.row())
            except Exception:
                track = None
        if track is not None and getattr(track, "removed", False):
            painter.setOpacity(0.4)
        else:
            painter.setOpacity(1.0)
        style = opt.widget.style() if opt.widget else QApplication.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, opt, painter, opt.widget)

        state = index.data(Qt.CheckStateRole)

        if not (opt.state & QStyle.State_Selected):
            if opt.state & QStyle.State_MouseOver:
                color = self.hover_color
            elif state == Qt.Checked:
                color = self.checked_color
            else:
                color = self.unchecked_color
            painter.fillRect(opt.rect, color)

        pen = opt.palette.highlightedText().color() if opt.state & QStyle.State_Selected else Qt.white
        painter.setPen(pen)
        text = "Keep" if state == Qt.Checked else "Skip"
        painter.drawText(opt.rect, Qt.AlignCenter, text)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease and option.rect.contains(event.pos()):
            current = index.data(Qt.CheckStateRole)
            new_state = Qt.Unchecked if current == Qt.Checked else Qt.Checked
            model.setData(index, new_state, Qt.CheckStateRole)
            return True
        return super().editorEvent(event, model, option, index)
