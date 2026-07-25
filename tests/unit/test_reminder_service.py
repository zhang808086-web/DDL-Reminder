from datetime import datetime, timedelta

from ddl_reminder.application.reminder_service import ReminderLevel, ReminderService
from ddl_reminder.domain.task import Task
from ddl_reminder.infrastructure.in_memory_task_repository import InMemoryTaskRepository

def make_task(title: str, deadline: datetime, **kwargs) -> Task:
    return Task(
        title=title,
        deadline=deadline,
        created_at=kwargs.pop("created_at", datetime(2026, 1, 1, 9, 0)),
        updated_at=kwargs.pop("updated_at", datetime(2026, 1, 1, 9, 0)),
        **kwargs,
    )
    
def test_returns_24h_reminder_for_task_with_one_day():
    now = datetime(2026,1,1,9,0)
    repo = InMemoryTaskRepository()
    
    task = repo.add(make_task("作业", now + timedelta(hours = 23)))
    
    service = ReminderService(repo)
    
    reminders = service.check_due_reminders(now)
    
    assert len(reminders) == 1
    assert reminders[0].task_id == task.id
    assert reminders[0].level == ReminderLevel.WITHIN_24H
    assert repo.get_by_id(task.id).notified_24h is True
    
def test_returns_1h_reminder_for_task_with_one_day():
    now = datetime(2026,1,1,9,0)
    repo = InMemoryTaskRepository()
    
    task = repo.add(make_task("作业", now + timedelta(hours = 1)))
    
    service = ReminderService(repo)
    
    reminders = service.check_due_reminders(now)
    
    assert len(reminders) == 1
    assert reminders[0].task_id == task.id
    assert reminders[0].level == ReminderLevel.WITHIN_1H
    assert repo.get_by_id(task.id).notified_24h is True
    assert repo.get_by_id(task.id).notified_1h is True

def test_completed_task_does_not_create_reminder():
    now = datetime(2026,1,1,9,0)
    repo = InMemoryTaskRepository()
    repo.add(make_task("作业", now + timedelta(hours = 1), is_completed = True))
    
    service = ReminderService(repo)
    
    reminders = service.check_due_reminders(now)
    assert reminders == []
    
def test_task_already_notified_24h_does_not_create_24h_reminder():
    now = datetime(2026,1,1,9,0)
    repo = InMemoryTaskRepository()
    task = repo.add(make_task("作业", now + timedelta(hours=23), notified_24h = True))
    
    service = ReminderService(repo)
    reminders = service.check_due_reminders(now)
    
    assert reminders == []
    assert repo.get_by_id(task.id).notified_24h is True
    
def test_task_already_notified_1h_does_not_create_1h_reminder():
    now = datetime(2026, 1, 1, 9, 0)
    repo = InMemoryTaskRepository()
    task = repo.add(
        make_task(
            "作业",
            now + timedelta(minutes=30),
            notified_1h=True,
            notified_24h=True,
        )
    )

    service = ReminderService(repo)

    reminders = service.check_due_reminders(now)

    assert reminders == []
    assert repo.get_by_id(task.id).notified_1h is True


def test_overdue_task_creates_overdue_reminder():
    now = datetime(2026, 1, 1, 9, 0)
    repo = InMemoryTaskRepository()
    task = repo.add(make_task("作业", now - timedelta(minutes=10)))

    service = ReminderService(repo)

    reminders = service.check_due_reminders(now)

    assert len(reminders) == 1
    assert reminders[0].task_id == task.id
    assert reminders[0].level == ReminderLevel.OVERDUE
    assert repo.get_by_id(task.id).notified_overdue is True


def test_task_already_notified_1h_still_creates_overdue_reminder_after_deadline():
    now = datetime(2026, 1, 1, 9, 0)
    repo = InMemoryTaskRepository()
    task = repo.add(
        make_task(
            "作业",
            now - timedelta(minutes=10),
            notified_1h=True,
            notified_24h=True,
            notified_overdue=False,
        )
    )

    service = ReminderService(repo)

    reminders = service.check_due_reminders(now)

    assert len(reminders) == 1
    assert reminders[0].task_id == task.id
    assert reminders[0].level == ReminderLevel.OVERDUE
    assert repo.get_by_id(task.id).notified_overdue is True


def test_task_already_notified_overdue_does_not_create_overdue_reminder_again():
    now = datetime(2026, 1, 1, 9, 0)
    repo = InMemoryTaskRepository()
    task = repo.add(
        make_task(
            "作业",
            now - timedelta(minutes=10),
            notified_overdue=True,
        )
    )

    service = ReminderService(repo)

    reminders = service.check_due_reminders(now)

    assert reminders == []
    assert repo.get_by_id(task.id).notified_overdue is True


def test_task_more_than_24h_away_does_not_create_reminder():
    now = datetime(2026, 1, 1, 9, 0)
    repo = InMemoryTaskRepository()
    task = repo.add(make_task("作业", now + timedelta(hours=25)))

    service = ReminderService(repo)

    reminders = service.check_due_reminders(now)

    assert reminders == []
    saved_task = repo.get_by_id(task.id)
    assert saved_task.notified_24h is False
    assert saved_task.notified_1h is False
    assert saved_task.notified_overdue is False
    
