from datetime import datetime,date,time
from typing import TYPE_CHECKING

from ddl_reminder.domain.task import Task
from ddl_reminder.domain.deadline import normalize_deadline

if TYPE_CHECKING:
    from ddl_reminder.ports.task_repository import TaskRepository
    
class TaskService:
    def __init__(self, task_repository: 'TaskRepository'):
        self.repo = task_repository
    
    def _get_now(self,now: datetime | None) -> datetime:
        if now is None:
            return datetime.now()
        return now
    
    def create_task(
        self, 
        title: str,
        deadline_date: date,
        deadline_time: time | None = None,
        description: str = '',
        now: datetime | None = None
        ) -> Task:
        current_time = self._get_now(now)
        deadline = normalize_deadline(deadline_date, deadline_time)
        task = Task(
            title = title,
            description = description,
            deadline = deadline,
            created_at = current_time,
            updated_at = current_time
        )
        
        return self.repo.add(task)
    
    def update_task(
        self, 
        task_id: int,
        title: str | None = None,
        deadline_date: date | None = None,
        deadline_time: time | None = None,
        description: str | None = None,
        now: datetime | None = None
    ) -> Task:
        current_time = self._get_now(now)
        task = self.repo.get_by_id(task_id)

        # Update task attributes if provided
        if title is not None:
            task.rename(title, current_time)
        if description is not None:
            task.description = description
        if deadline_date is not None or deadline_time is not None:
            new_deadline = normalize_deadline(
                deadline_date or task.deadline.date(),
                deadline_time or task.deadline.time()
            )
            if new_deadline != task.deadline:
                task.deadline = new_deadline
                task.notified_1h = False
                task.notified_24h = False
                task.notified_overdue = False

        task.updated_at = current_time
        return self.repo.update(task)
    
    def complete_task(self, task_id: int, now: datetime | None = None) -> Task:
        current_time = self._get_now(now)
        task = self.repo.get_by_id(task_id)

        task.mark_completed(current_time)
        return self.repo.update(task)

    def restore_task(self, task_id: int, now: datetime | None = None) -> Task:
        current_time = self._get_now(now)
        task = self.repo.get_by_id(task_id)

        task.restore(current_time)
        return self.repo.update(task)
    
    def delete_task(self, task_id: int) -> None:
        self.repo.delete(task_id)
        
    def get_task(self, task_id: int) -> Task:
        return self.repo.get_by_id(task_id)
    
    def list_active_tasks(self) -> list[Task]:
        tasks = self.repo.list_all()
        active_tasks = [task for task in tasks if not task.is_completed]
        return active_tasks
    
    def list_completed_tasks(self) -> list[Task]:
        tasks = self.repo.list_all()
        completed_tasks = [task for task in tasks if task.is_completed]
        return completed_tasks
    
    def get_urgent_tasks(self, limit:int = 3) -> list[Task]:
        tasks = self.repo.list_all()
        urgent_tasks = [
            task for task in tasks 
            if not task.is_completed
        ]
        urgent_tasks.sort(key=lambda task: (task.deadline, task.created_at))
        return urgent_tasks[:limit]
