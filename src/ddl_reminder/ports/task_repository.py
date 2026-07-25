from typing import Protocol

from ddl_reminder.domain.task import Task


class TaskRepository(Protocol):
    def add(self, task: Task) -> Task:
        pass

    def update(self, task: Task) -> Task:
        pass

    def get_by_id(self, task_id: int) -> Task:
        pass

    def list_all(self) -> list[Task]:
        pass

    def delete(self, task_id: int) -> None:
        pass
