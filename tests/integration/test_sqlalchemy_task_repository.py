from datetime import datetime

import pytest

from ddl_reminder.domain.exceptions import TaskNotFoundError
from ddl_reminder.domain.task import Task
from ddl_reminder.infrastructure.database import (
    create_session_factory,
    create_sqlite_engine,
    init_database,
)
from ddl_reminder.infrastructure.sqlalchemy_task_repository import SQLAlchemyTaskRepository


@pytest.fixture
def repository() -> SQLAlchemyTaskRepository:
    engine = create_sqlite_engine("sqlite:///:memory:")
    init_database(engine)
    session_factory = create_session_factory(engine)
    return SQLAlchemyTaskRepository(session_factory)


def make_task(title: str = "Test Task") -> Task:
    return Task(
        title=title,
        description="Test Description",
        deadline=datetime(2026, 7, 21, 23, 59),
        created_at=datetime(2026, 7, 20, 12, 0),
        updated_at=datetime(2026, 7, 20, 12, 0),
    )


def assert_same_task(actual: Task, expected: Task) -> None:
    assert actual.id == expected.id
    assert actual.title == expected.title
    assert actual.description == expected.description
    assert actual.deadline == expected.deadline
    assert actual.is_completed == expected.is_completed
    assert actual.completed_at == expected.completed_at
    assert actual.notified_24h == expected.notified_24h
    assert actual.notified_1h == expected.notified_1h
    assert actual.created_at == expected.created_at
    assert actual.updated_at == expected.updated_at


def test_add_assigns_database_id(repository: SQLAlchemyTaskRepository):
    task = make_task()

    added_task = repository.add(task)

    assert added_task.id == 1


def test_add_overwrites_existing_task_id(repository: SQLAlchemyTaskRepository):
    task = make_task()
    task.id = 999

    added_task = repository.add(task)

    assert added_task.id == 1
    assert_same_task(repository.get_by_id(1), added_task)


def test_get_by_id_returns_complete_task(repository: SQLAlchemyTaskRepository):
    task = make_task()
    task.is_completed = True
    task.completed_at = datetime(2026, 7, 20, 13, 0)
    task.notified_24h = True
    task.notified_1h = True

    added_task = repository.add(task)
    retrieved_task = repository.get_by_id(added_task.id)

    assert_same_task(retrieved_task, added_task)


def test_get_by_id_raises_error_for_nonexistent_task(
    repository: SQLAlchemyTaskRepository,
):
    with pytest.raises(TaskNotFoundError):
        repository.get_by_id(999)


def test_list_all_returns_all_tasks(repository: SQLAlchemyTaskRepository):
    first_task = repository.add(make_task("Task 1"))
    second_task = repository.add(make_task("Task 2"))

    all_tasks = repository.list_all()

    assert all_tasks == [first_task, second_task]


def test_update_persists_complete_task_state(repository: SQLAlchemyTaskRepository):
    added_task = repository.add(make_task())
    added_task.title = "Updated Title"
    added_task.description = "Updated Description"
    added_task.deadline = datetime(2026, 7, 22, 10, 30)
    added_task.is_completed = True
    added_task.completed_at = datetime(2026, 7, 21, 9, 0)
    added_task.notified_24h = True
    added_task.notified_1h = True
    added_task.updated_at = datetime(2026, 7, 21, 9, 30)

    updated_task = repository.update(added_task)
    reloaded_task = repository.get_by_id(updated_task.id)

    assert_same_task(reloaded_task, updated_task)


def test_update_raises_error_for_nonexistent_task(
    repository: SQLAlchemyTaskRepository,
):
    task = make_task()
    task.id = 999

    with pytest.raises(TaskNotFoundError):
        repository.update(task)


def test_delete_removes_task(repository: SQLAlchemyTaskRepository):
    added_task = repository.add(make_task())

    repository.delete(added_task.id)

    with pytest.raises(TaskNotFoundError):
        repository.get_by_id(added_task.id)


def test_delete_raises_error_for_nonexistent_task(
    repository: SQLAlchemyTaskRepository,
):
    with pytest.raises(TaskNotFoundError):
        repository.delete(999)


def test_add_allows_tasks_with_same_title(repository: SQLAlchemyTaskRepository):
    first_task = repository.add(make_task("Duplicate"))
    second_task = repository.add(make_task("Duplicate"))

    assert first_task.id != second_task.id
