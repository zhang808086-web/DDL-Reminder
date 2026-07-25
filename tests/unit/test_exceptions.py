import pytest
from ddl_reminder.domain.exceptions import(
    TaskError,
    TaskNotFoundError,
    InvalidTaskTitleError,
    InvalidDeadlineError
)

def test_task_error():
    with pytest.raises(TaskError):
        raise TaskError("Test error")

def test_task_not_found_error():
    with pytest.raises(TaskNotFoundError):
        raise TaskNotFoundError("Test not found error")
    assert issubclass(TaskNotFoundError, TaskError)

def test_invalid_task_title_error():
    with pytest.raises(InvalidTaskTitleError):
        raise InvalidTaskTitleError("Test invalid title error")
    assert issubclass(InvalidTaskTitleError, TaskError)

def test_invalid_deadline_error():
    with pytest.raises(InvalidDeadlineError):
        raise InvalidDeadlineError("Test invalid deadline error")
    assert issubclass(InvalidDeadlineError, TaskError)
