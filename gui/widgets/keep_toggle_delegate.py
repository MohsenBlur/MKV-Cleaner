from PySide6.QtWidgets import QStyledItemDelegate, QStyle
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
        painter.save()
        state = index.data(Qt.CheckStateRole)
        if option.state & QStyle.State_MouseOver:
            color = self.hover_color
        elif state == Qt.Checked:
            color = self.checked_color
        else:
            color = self.unchecked_color
        painter.fillRect(option.rect, color)
        painter.setPen(Qt.white)
        text = "Keep" if state == Qt.Checked else "Skip"
        painter.drawText(option.rect, Qt.AlignCenter, text)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease and option.rect.contains(event.pos()):
            current = index.data(Qt.CheckStateRole)
            new_state = Qt.Unchecked if current == Qt.Checked else Qt.Checked
            model.setData(index, new_state, Qt.CheckStateRole)
            return True
        return super().editorEvent(event, model, option, index)
