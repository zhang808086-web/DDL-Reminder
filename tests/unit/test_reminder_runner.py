from datetime import datetime

from ddl_reminder.application.reminder_runner import ReminderRunner
from ddl_reminder.application.reminder_service import Reminder, ReminderLevel


def make_reminder(task_id: int, level: ReminderLevel = ReminderLevel.WITHIN_24H) -> Reminder:
    return Reminder(
        task_id=task_id,
        title=f"task-{task_id}",
        message=f"task-{task_id} reminder",
        level=level,
    )


class FakeReminderService:
    def __init__(self, reminders: list[Reminder]) -> None:
        self.reminders = reminders
        self.received_now = None

    def check_due_reminders(self, now=None) -> list[Reminder]:
        self.received_now = now
        return self.reminders


class FakeNotifier:
    def __init__(self) -> None:
        self.sent: list[Reminder] = []

    def notify(self, reminder: Reminder) -> None:
        self.sent.append(reminder)


class FailingNotifier:
    def __init__(self, failed_task_id: int) -> None:
        self.failed_task_id = failed_task_id
        self.sent: list[Reminder] = []

    def notify(self, reminder: Reminder) -> None:
        self.sent.append(reminder)
        if reminder.task_id == self.failed_task_id:
            raise RuntimeError("notify failed")


class FakeLogger:
    def __init__(self) -> None:
        self.exceptions: list[tuple[str, tuple[object, ...]]] = []

    def exception(self, message: str, *args) -> None:
        self.exceptions.append((message, args))


def test_run_once_sends_all_reminders_to_notifier():
    reminders = [make_reminder(1), make_reminder(2, ReminderLevel.WITHIN_1H)]
    reminder_service = FakeReminderService(reminders)
    notifier = FakeNotifier()
    logger = FakeLogger()
    runner = ReminderRunner(reminder_service, notifier, logger)

    runner.run_once()

    assert notifier.sent == reminders
    assert logger.exceptions == []


def test_run_once_passes_now_to_reminder_service():
    now = datetime(2026, 1, 1, 9, 0)
    reminder_service = FakeReminderService([])
    notifier = FakeNotifier()
    logger = FakeLogger()
    runner = ReminderRunner(reminder_service, notifier, logger)

    runner.run_once(now)

    assert reminder_service.received_now == now


def test_run_once_logs_exception_when_notification_fails():
    reminders = [make_reminder(1)]
    reminder_service = FakeReminderService(reminders)
    notifier = FailingNotifier(failed_task_id=1)
    logger = FakeLogger()
    runner = ReminderRunner(reminder_service, notifier, logger)

    runner.run_once()

    assert len(logger.exceptions) == 1
    message, args = logger.exceptions[0]
    assert message == "Failed to send reminder: task_id=%s, level=%s"
    assert args == (1, ReminderLevel.WITHIN_24H.value)


def test_run_once_continues_after_notification_failure():
    reminders = [make_reminder(1), make_reminder(2)]
    reminder_service = FakeReminderService(reminders)
    notifier = FailingNotifier(failed_task_id=1)
    logger = FakeLogger()
    runner = ReminderRunner(reminder_service, notifier, logger)

    runner.run_once()

    assert notifier.sent == reminders
    assert len(logger.exceptions) == 1
