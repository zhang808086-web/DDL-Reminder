from __future__ import annotations
from dataclasses  import dataclass 
from enum import Enum
from ddl_reminder.ports.task_repository import TaskRepository
from datetime import datetime

from ddl_reminder.domain.deadline import DeadlineCategory, classify_deadline


class ReminderLevel(Enum):
    WITHIN_24H = "24h"
    WITHIN_1H = "1h"
    OVERDUE = "overdue"

@dataclass
class Reminder:
    task_id: int
    title: str
    message: str
    level: ReminderLevel
    

class ReminderService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repo = repository
    
    def check_due_reminders(self, now: datetime | None = None) -> list[Reminder]:
        if now is None:
            now = datetime.now()
            
        reminders: list[Reminder] = []
        
        for task in self._repo.list_all():
            if task.is_completed:
                continue
            
            category, _seconds_diff = classify_deadline(task.deadline, now)
            
            if category == DeadlineCategory.OVERDUE:
                reminder = self._build_overdue_reminder_if_needed(task)   
            elif category == DeadlineCategory.WITHIN_ONE_HOUR:
                reminder = self._build_1h_reminder_if_needed(task)
            elif category == DeadlineCategory.WITHIN_ONE_DAY:
                reminder = self._build_24h_reminder_if_needed(task)
            else:
                reminder = None

            if reminder is None:
                continue
            
            self._repo.update(task)
            reminders.append(reminder)
        
        return reminders
    
    def _build_overdue_reminder_if_needed(self, task) -> Reminder | None:
        if task.notified_overdue is True:
            return None
        
        task.notified_overdue = True
        
        return Reminder(
            task_id = task.id,
            title = task.title,
            message = f"任务 {task.title} 已逾期",
            level = ReminderLevel.OVERDUE
        )
        
    def _build_1h_reminder_if_needed(self, task) -> Reminder | None:
        if task.notified_1h is True:
            return None
        
        task.notified_1h = True
        task.notified_24h = True
        
        return Reminder(
            task_id = task.id,
            title = task.title,
            message = f"任务 {task.title} 将在 1 小时内截止",
            level = ReminderLevel.WITHIN_1H
        )
        
    def _build_24h_reminder_if_needed(self, task) -> Reminder | None:
        if task.notified_24h is True:
            return None
        
        task.notified_24h = True
        
        return Reminder(
            task_id = task.id,
            title = task.title,
            message = f"任务 {task.title} 将在 24 小时内截止",
            level = ReminderLevel.WITHIN_24H
        )
        
        
        

                
        
    
