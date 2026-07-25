import pytest
from datetime import datetime

from ddl_reminder.domain.exceptions import TaskNotFoundError
from ddl_reminder.domain.task import Task
from ddl_reminder.infrastructure.in_memory_task_repository import InMemoryTaskRepository

def make_task(title= "Test Task") -> Task:
    return Task(
        title = title,
        description = "Test Description",
        deadline = datetime(2026,7,21,23,59)
    )
    
def test_add_assigns_task():
    repository = InMemoryTaskRepository()
    task = make_task()
    added_task = repository.add(task)
    assert added_task.id == 1

def test_add_assigns_incrementing_ids():
    repository = InMemoryTaskRepository()
    task1 = make_task("Task 1")
    task2 = make_task("Task 2")
    added_task1 = repository.add(task1)
    added_task2 = repository.add(task2)
    assert added_task1.id == 1
    assert added_task2.id == 2
    
def test_add_overwrites_existing_task_id():
    repository = InMemoryTaskRepository()
    task = make_task()
    task.id = 999
    added_task = repository.add(task)
    assert added_task.id == 1  # The repository should assign a new ID, not use the existing one
    assert repository.get_by_id(1) == added_task

def test_get_by_id_returns_correct_task():
    repository = InMemoryTaskRepository()
    task = make_task()
    added_task = repository.add(task)
    retrieved_task = repository.get_by_id(added_task.id)
    assert retrieved_task == added_task

def test_get_by_id_raises_error_for_nonexistent_task():
    repository = InMemoryTaskRepository()
    with pytest.raises(TaskNotFoundError):
        repository.get_by_id(999)

def test_update_task():
    repository = InMemoryTaskRepository()
    task = make_task()
    added_task = repository.add(task)
    added_task.title = "Updated Task"
    updated_task = repository.update(added_task)
    assert updated_task.title == "Updated Task"

def test_update_raises_error_for_nonexistent_task():
    repository = InMemoryTaskRepository()
    task = make_task()
    task.id = 999  # Non-existent ID
    with pytest.raises(TaskNotFoundError):
        repository.update(task)

def test_list_all_returns_all_tasks():
    repository = InMemoryTaskRepository()
    task1 = make_task("Task 1")
    task2 = make_task("Task 2")
    repository.add(task1)
    repository.add(task2)
    all_tasks = repository.list_all()
    assert len(all_tasks) == 2
    assert all_tasks[0].title == "Task 1"
    assert all_tasks[1].title == "Task 2"

def test_delete_task():
    repository = InMemoryTaskRepository()
    task = make_task()
    added_task = repository.add(task)
    repository.delete(added_task.id)
    with pytest.raises(TaskNotFoundError):
        repository.get_by_id(added_task.id)

def test_delete_raises_error_for_nonexistent_task():
    repository = InMemoryTaskRepository()
    with pytest.raises(TaskNotFoundError):
        repository.delete(999)

def test_add_task_with_same_title():
    repository = InMemoryTaskRepository()
    task1 = make_task("Duplicate Task")
    task2 = make_task("Duplicate Task")
    added_task1 = repository.add(task1)
    added_task2 = repository.add(task2)
    assert added_task1.id != added_task2.id

def test_update_task_with_no_changes():
    repository = InMemoryTaskRepository()
    task = make_task()
    added_task = repository.add(task)
    
    # Update the task without making any changes
    updated_task = repository.update(added_task)
    
    assert updated_task == added_task 

    
    
    
    
    
    
    
    
    