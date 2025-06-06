try:
    from PySide6.QtWidgets import QGraphicsOpacityEffect
except Exception:  # PySide6 may be stubbed in tests
    QGraphicsOpacityEffect = None


def apply_fade_on_disable(widget, disabled_opacity=0.4):
    """Add an opacity effect that fades the widget when disabled."""
    if QGraphicsOpacityEffect is None:
        return
    if not hasattr(widget, "setGraphicsEffect") or not hasattr(widget, "enabledChanged"):
        return

    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    effect.setOpacity(1.0 if widget.isEnabled() else disabled_opacity)

    def _update(enabled):
        effect.setOpacity(1.0 if enabled else disabled_opacity)

    widget.enabledChanged.connect(_update)
