from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle, QApplication
from PySide6.QtCore import Qt, QRect

class FlagDelegate(QStyledItemDelegate):
    """Paint current and original flag icons side by side."""

    def __init__(self, column: int, parent=None):
        super().__init__(parent)
        self.column = column

    def paint(self, painter, option, index):
        model = index.model()
        track = model.track_at_row(index.row())
        if self.column == 5:
            char = "🚩"
            cur = bool(index.data(model.ForcedRole))
            orig = bool(index.data(model.OrigForcedRole))
        else:
            char = "🔊" if track.type == "audio" else "CC"
            cur = bool(index.data(model.DefaultRole))
            orig = bool(index.data(model.OrigDefaultRole))

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        # Remove focus state so cells don't show selection outlines
        opt.state &= ~QStyle.State_HasFocus

        painter.save()
        style = opt.widget.style() if opt.widget else QApplication.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, opt, painter, opt.widget)

        rect = opt.rect
        color = opt.palette.highlightedText().color() if opt.state & QStyle.State_Selected else opt.palette.text().color()
        faded_opacity = 0.3
        if cur and orig:
            half = rect.width() // 2
            orig_rect = QRect(rect.left(), rect.top(), half, rect.height())
            cur_rect = QRect(rect.left() + half, rect.top(), rect.width() - half, rect.height())
            painter.setPen(color)
            painter.setOpacity(faded_opacity)
            painter.drawText(orig_rect, Qt.AlignCenter, char)
            painter.setOpacity(1.0)
            painter.drawText(cur_rect, Qt.AlignCenter, char)
        elif orig and not cur:
            painter.setPen(color)
            if self.column == 5:
                painter.setOpacity(faded_opacity)
                painter.drawText(rect, Qt.AlignCenter, char)
            else:
                painter.setOpacity(faded_opacity)
                painter.drawText(rect, Qt.AlignCenter, char)
        elif cur:
            painter.setPen(color)
            painter.setOpacity(1.0)
            painter.drawText(rect, Qt.AlignCenter, char)
        painter.restore()
