from PySide6.QtWidgets import QSystemTrayIcon

from ddl_reminder.application.reminder_service import Reminder, ReminderLevel

class DesktopNotifier:
    def __init__(self, tray_icon: QSystemTrayIcon) -> None:
        self._tray_icon = tray_icon
        
    def notify(self, reminder: Reminder) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise RuntimeError("System tray is not available")
        
        
        title = self._build_title(reminder)
        
        self._tray_icon.showMessage(
            title,
            reminder.message,
            QSystemTrayIcon.Information,
            10_000
        )
        
        if not self._tray_icon.supportsMessages():
            raise RuntimeError("System tray messages are not supported")
        
    def _build_title(self, reminder: Reminder) -> str:
        if reminder.level == ReminderLevel.OVERDUE:
            return 'DDL 已逾期'
        
        if reminder.level == ReminderLevel.WITHIN_1H:
            return "DDL 1 小时提醒"
        
        if reminder.level == ReminderLevel.WITHIN_24H:
            return "DDL 24 小时提醒"
        
        return "DDL Reminder"
