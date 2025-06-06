from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)
from PySide6.QtGui import QPainter

class NoFocusDelegate(QStyledItemDelegate):
    """Delegate that removes the focus outline from table cells."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        opt = QStyleOptionViewItem(option)
        opt.state &= ~QStyle.State_HasFocus
        super().paint(painter, opt, index)
