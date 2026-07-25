import pytest
from dataclasses import dataclass, field
from datetime import datetime
from ddl_reminder.domain.exceptions import InvalidTaskTitleError, InvalidDeadlineError

from ddl_reminder.domain.task import Task

def test_create_task_with_valid_title_and_deadline():
    title = "Test Task"
    deadline = datetime(2026, 7, 17, 23, 59)

    task = Task(title=title, deadline=deadline)

    assert task.title == title
    assert task.deadline == deadline

def test_create_task_with_invalid_title():
    with pytest.raises(InvalidTaskTitleError):
        Task(title="", deadline=datetime(2026, 7, 17, 23, 59))
        
def test_create_task_with_toolong_title():
    with pytest.raises(InvalidTaskTitleError):
        Task(title="This is a way too long title for a taskaaaaaa", deadline=datetime(2026, 7, 17, 23, 59))

def test_create_task_with_invalid_deadline():
    with pytest.raises(InvalidDeadlineError):
        Task(title="Test Task", deadline=None)

def test_create_task_with_valid_id():
    title = "Test Task"
    deadline = datetime(2026, 7, 17, 23, 59)

    task = Task(title=title, deadline=deadline)

    assert task.id is None

def test_create_task_with_valid_completed_at():
    title = "Test Task"
    deadline = datetime(2026, 7, 17, 23, 59)

    task = Task(title=title, deadline=deadline)

    assert task.completed_at is None

def test_create_task_with_valid_is_completed():
    title = "Test Task"
    deadline = datetime(2026, 7, 17, 23, 59)

    task = Task(title=title, deadline=deadline)

    assert task.is_completed is False

def test_create_task_with_valid_notified():
    title = "Test Task"
    deadline = datetime(2026, 7, 17, 23, 59)

    task = Task(title=title, deadline=deadline)

    assert task.notified_24h is False
    assert task.notified_1h is False
    
def test_create_task_with_valid_created_at_updated_at():
    title = "Test Task"
    deadline = datetime(2026, 7, 17, 23, 59)

    task = Task(title=title, deadline=deadline)

    assert task.created_at is not None
    assert task.updated_at is not None
    
def test_mark_completed_sets_is_completed_and_completed_at():
    now = datetime(2026,7,17,12,0)
    task = Task(title="Test Task", description = None,deadline=datetime(2026, 7, 20, 23, 59))
    
    task.mark_completed(now)
    
    assert task.is_completed is True
    assert task.completed_at == now
    assert task.updated_at == now

def test_mark_completed_is_idempotent():
    first_time = datetime(2026,7,17,12,0)
    second_time = datetime(2026,7,18,12,0)
    task = Task(title = 'Test Task', description = None, deadline = datetime(2026,7,20,23,59))
    task.mark_completed(first_time)
    
    task.mark_completed(second_time)
    
    assert task.is_completed is True
    assert task.completed_at == first_time
    
def test_restore_clears_completed_status():
    now = datetime(2026,7,18,12,0)
    task = Task(title = 'Test Task', description = None, deadline = datetime(2026,7,20,23,59))
    task.mark_completed(datetime(2026,7,17,12,0))
    
    task.restore(datetime(2026,7,17,23,0))
    
    assert task.is_completed is False
    assert task.completed_at is None
    assert task.updated_at == datetime(2026,7,17,23,0)

def test_restore_resets_notification_flags():
    task = Task(title = 'Test Task', description = None, deadline = datetime(2026,7,20,23,59))
    task.notified_24h = True
    task.notified_1h = True
    task.mark_completed(datetime(2026,7,17,12,0))

    task.restore(datetime(2026,7,17,23,0))

    assert task.notified_24h is False
    assert task.notified_1h is False

def test_restore_on_active_task_does_nothing():
    task = Task(title = 'Test Task', description = None, deadline = datetime(2026,7,20,23,59))
    task.notified_24h = True
    task.notified_1h = True
    task.mark_completed(datetime(2026,7,17,12,0))

    task.restore(datetime(2026,7,18,12,0))

    assert task.is_completed is False
    assert task.completed_at is None
    assert task.updated_at == datetime(2026,7,18,12,0)
