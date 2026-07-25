from __future__ import annotations
import logging
from datetime import datetime

from ddl_reminder.application.reminder_service import ReminderService
from ddl_reminder.ports.notifier import Notifier


class ReminderRunner:
    def __init__(self, 
                 reminder_service: ReminderService,
                 notifier: Notifier,
                 logger: logging.Logger | None = None
    ) -> None:
        self._reminder_service = reminder_service
        self._notifier = notifier
        self._logger = logger or logging.getLogger(__name__)
        

    def run_once(self, now: datetime | None = None) -> None:
        reminders = self._reminder_service.check_due_reminders(now)
        
        for reminder in reminders:
            try:
                self._notifier.notify(reminder)
            except Exception:
                self._logger.exception(
                    "Failed to send reminder: task_id=%s, level=%s",
                    reminder.task_id,
                    reminder.level.value
                )
                
        