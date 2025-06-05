from PySide6.QtWidgets import QProxyStyle, QStyle


class FastToolTipStyle(QProxyStyle):
    """Style proxy that reduces the delay before tooltips show."""

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_ToolTip_WakeUpDelay:
            return 100  # show tooltips quickly
        return super().styleHint(hint, option, widget, returnData)
