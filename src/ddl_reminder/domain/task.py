from dataclasses import dataclass, field
from datetime import datetime

from ddl_reminder.domain.exceptions import InvalidDeadlineError, InvalidTaskTitleError


@dataclass
class Task:
    title: str
    deadline: datetime
    description: str | None = None
    is_completed: bool = False

    id: int | None = None
    completed_at: datetime | None = None
    notified_24h: bool = False
    notified_1h: bool = False
    notified_overdue: bool = False

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.title is None:
            raise InvalidTaskTitleError("Task title cannot be None")
        if len(self.title.strip()) == 0:
            raise InvalidTaskTitleError("Task title cannot be empty")
        if len(self.title.strip()) > 15:
            raise InvalidTaskTitleError("Task title cannot be longer than 15 characters")
        if self.deadline is None:
            raise InvalidDeadlineError("Task deadline cannot be None")

    def mark_completed(self, now: datetime) -> None:
        if self.is_completed:
            return
        self.is_completed = True
        self.completed_at = now
        self.updated_at = now

    def restore(self, now: datetime) -> None:
        if not self.is_completed:
            return
        self.is_completed = False
        self.completed_at = None
        self.updated_at = now
        self.notified_24h = False
        self.notified_1h = False
        self.notified_overdue = False

    def rename(self,title: str, now: datetime) -> None:
        old_title = self.title
        self.title = title
        try:
            self.__post_init__()
        except Exception:
            self.title = old_title
            raise
        self.updated_at = now
        
