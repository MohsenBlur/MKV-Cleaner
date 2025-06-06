from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PySide6.QtGui import QPainter
from PySide6.QtCore import QStyle

class NoFocusDelegate(QStyledItemDelegate):
    """Delegate that removes the focus outline from table cells."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        opt = QStyleOptionViewItem(option)
        opt.state &= ~QStyle.State_HasFocus
        super().paint(painter, opt, index)
