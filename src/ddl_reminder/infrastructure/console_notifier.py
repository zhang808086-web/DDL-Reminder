
from ddl_reminder.application.reminder_service import Reminder
from ddl_reminder.ports.notifier import Notifier

class ConsoleNotifier(Notifier):
    def notify(self, reminder: Reminder) -> None:
        print(reminder.message)

