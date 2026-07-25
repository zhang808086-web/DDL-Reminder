from datetime import date, datetime, time

import pytest

from ddl_reminder.application.task_service import TaskService
from ddl_reminder.domain.exceptions import InvalidTaskTitleError, TaskNotFoundError
from ddl_reminder.infrastructure.in_memory_task_repository import InMemoryTaskRepository


@pytest.fixture
def repo() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()


@pytest.fixture
def service(repo: InMemoryTaskRepository) -> TaskService:
    return TaskService(repo)


def test_create_task_saves_task_with_normalized_deadline(
    service: TaskService,
    repo: InMemoryTaskRepository,
):
    now = datetime(2026, 7, 21, 12, 0)

    task = service.create_task(
        title="Test Task",
        deadline_date=date(2026, 7, 22),
        description="Test Description",
        now=now,
    )

    assert task.id == 1
    assert task.deadline == datetime(2026, 7, 22, 23, 59)
    assert task.created_at == now
    assert task.updated_at == now
    assert repo.get_by_id(task.id) == task


def test_create_task_uses_given_deadline_time(service: TaskService):
    task = service.create_task(
        title="Test Task",
        deadline_date=date(2026, 7, 22),
        deadline_time=time(10, 30),
    )

    assert task.deadline == datetime(2026, 7, 22, 10, 30)


def test_update_task_can_change_title_description_and_deadline(service: TaskService):
    task = service.create_task(
        title="Old Task",
        deadline_date=date(2026, 7, 22),
        description="old",
    )
    now = datetime(2026, 7, 21, 13, 0)

    updated = service.update_task(
        task.id,
        title="New Task",
        description="new",
        deadline_date=date(2026, 7, 23),
        deadline_time=time(9, 15),
        now=now,
    )

    assert updated.title == "New Task"
    assert updated.description == "new"
    assert updated.deadline == datetime(2026, 7, 23, 9, 15)
    assert updated.updated_at == now


def test_update_task_rejects_invalid_title_and_keeps_old_title(service: TaskService):
    task = service.create_task(
        title="Valid",
        deadline_date=date(2026, 7, 22),
    )

    with pytest.raises(InvalidTaskTitleError):
        service.update_task(task.id, title="")

    assert service.get_task(task.id).title == "Valid"


def test_update_task_resets_notifications_only_when_deadline_changes(
    service: TaskService,
):
    task = service.create_task(
        title="Test Task",
        deadline_date=date(2026, 7, 22),
    )
    task.notified_1h = True
    task.notified_24h = True

    service.update_task(task.id, description="changed")

    assert task.notified_1h is True
    assert task.notified_24h is True

    service.update_task(task.id, deadline_date=date(2026, 7, 23))

    assert task.notified_1h is False
    assert task.notified_24h is False


def test_complete_task_marks_task_completed(service: TaskService):
    task = service.create_task("Test Task", date(2026, 7, 22))
    now = datetime(2026, 7, 21, 14, 0)

    completed = service.complete_task(task.id, now)

    assert completed.is_completed is True
    assert completed.completed_at == now
    assert completed.updated_at == now


def test_restore_task_marks_task_active(service: TaskService):
    task = service.create_task("Test Task", date(2026, 7, 22))
    service.complete_task(task.id, datetime(2026, 7, 21, 14, 0))
    now = datetime(2026, 7, 21, 15, 0)

    restored = service.restore_task(task.id, now)

    assert restored.is_completed is False
    assert restored.completed_at is None
    assert restored.updated_at == now


def test_delete_task_removes_task(service: TaskService):
    task = service.create_task("Test Task", date(2026, 7, 22))

    service.delete_task(task.id)

    with pytest.raises(TaskNotFoundError):
        service.get_task(task.id)


def test_list_active_tasks_excludes_completed_tasks(service: TaskService):
    active = service.create_task("Active", date(2026, 7, 22))
    completed = service.create_task("Done", date(2026, 7, 23))
    service.complete_task(completed.id, datetime(2026, 7, 21, 14, 0))

    active_tasks = service.list_active_tasks()

    assert active in active_tasks
    assert completed not in active_tasks


def test_list_completed_tasks_excludes_active_tasks(service: TaskService):
    active = service.create_task("Active", date(2026, 7, 22))
    completed = service.create_task("Done", date(2026, 7, 23))
    service.complete_task(completed.id, datetime(2026, 7, 21, 14, 0))

    completed_tasks = service.list_completed_tasks()

    assert completed in completed_tasks
    assert active not in completed_tasks


def test_get_urgent_tasks_returns_earliest_three_active_tasks(service: TaskService):
    task4 = service.create_task("Task 4", date(2026, 7, 25))
    task2 = service.create_task("Task 2", date(2026, 7, 23))
    task1 = service.create_task("Task 1", date(2026, 7, 22))
    task3 = service.create_task("Task 3", date(2026, 7, 24))

    urgent_tasks = service.get_urgent_tasks()

    assert urgent_tasks == [task1, task2, task3]
    assert task4 not in urgent_tasks


def test_get_urgent_tasks_uses_created_at_when_deadlines_match(service: TaskService):
    later = service.create_task(
        "Later",
        date(2026, 7, 22),
        now=datetime(2026, 7, 21, 12, 30),
    )
    earlier = service.create_task(
        "Earlier",
        date(2026, 7, 22),
        now=datetime(2026, 7, 21, 12, 0),
    )

    urgent_tasks = service.get_urgent_tasks(limit=2)

    assert urgent_tasks == [earlier, later]


def test_get_urgent_tasks_excludes_completed_tasks(service: TaskService):
    active = service.create_task("Active", date(2026, 7, 23))
    completed = service.create_task("Done", date(2026, 7, 22))
    service.complete_task(completed.id, datetime(2026, 7, 21, 14, 0))

    urgent_tasks = service.get_urgent_tasks()

    assert active in urgent_tasks
    assert completed not in urgent_tasks
