from ddl_reminder.domain.task import Task
from ddl_reminder.ports.task_repository import TaskRepository
from ddl_reminder.domain.exceptions import TaskNotFoundError

class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
    
    def add(self, task: Task) -> Task:
        task.id = self._next_id
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task
    
    def update(self, task: Task) -> Task:
        if task.id not in self._tasks:
            raise TaskNotFoundError(f"Task with id {task.id} not found.")
        self._tasks[task.id] = task
        return task
    
    def get_by_id(self, task_id: int) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with id {task_id} not found.")
        return self._tasks[task_id]
    
    def list_all(self) -> list[Task]:
        return list(self._tasks.values())
    
    def delete(self, task_id: int) -> None:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with id {task_id} not found.")
        del self._tasks[task_id]

    