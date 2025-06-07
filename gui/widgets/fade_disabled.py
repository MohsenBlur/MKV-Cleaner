"""Helper to fade widgets when they become disabled."""

try:
    from PySide6.QtWidgets import QGraphicsOpacityEffect
    from PySide6.QtCore import QObject, QEvent
except Exception:  # PySide6 may be stubbed in tests
    QGraphicsOpacityEffect = None
    QObject = object
    QEvent = None


def apply_fade_on_disable(widget, disabled_opacity=0.4):
    """Add an opacity effect that fades the widget when disabled."""
    if QGraphicsOpacityEffect is None:
        return
    if not hasattr(widget, "setGraphicsEffect") or not hasattr(widget, "installEventFilter"):
        return

    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    effect.setOpacity(1.0 if widget.isEnabled() else disabled_opacity)

    class _FadeFilter(QObject):
        def eventFilter(self, obj, event):
            if obj is widget and QEvent is not None and event.type() == QEvent.EnabledChange:
                effect.setOpacity(1.0 if widget.isEnabled() else disabled_opacity)
            return False

    filt = _FadeFilter(widget)
    widget.installEventFilter(filt)
    # Keep reference to avoid garbage collection
    if not hasattr(widget, "_fade_filters"):
        widget._fade_filters = []
    widget._fade_filters.append(filt)
