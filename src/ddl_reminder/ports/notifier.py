from typing import Protocol

from ddl_reminder.application.reminder_service import Reminder

class Notifier(Protocol):
    def notify(self, reminder: Reminder) -> None:
        ...