from ddl_reminder.domain.task import Task
from ddl_reminder.ports.task_repository import TaskRepository
from ddl_reminder.infrastructure.models import TaskModel
from ddl_reminder.domain.exceptions import TaskNotFoundError

class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def _to_model(self, task: Task, include_id: bool = False) -> TaskModel:
        model = TaskModel(
            title = task.title,
            description = task.description,
            deadline = task.deadline,
            is_completed = task.is_completed,
            completed_at = task.completed_at,
            notified_24h = task.notified_24h,
            notified_1h = task.notified_1h,
            notified_overdue = task.notified_overdue,
            created_at = task.created_at,
            updated_at = task.updated_at
        )
        
        if include_id:
            model.id = task.id
        
        return model 
    
    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id = model.id,
            title = model.title,
            description = model.description,
            deadline = model.deadline,
            is_completed = model.is_completed,
            completed_at = model.completed_at,
            notified_24h = model.notified_24h,
            notified_1h = model.notified_1h,
            notified_overdue = model.notified_overdue,
            created_at = model.created_at,
            updated_at = model.updated_at
        )

    def  get_by_id(self, task_id: int) -> Task:
        with self.session_factory() as session:
            model = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if model is None:
                raise TaskNotFoundError(f"Task with id {task_id} not found.")
            return self._to_domain(model)
    
    def add(self, task: Task) -> Task:
        with self.session_factory() as session:
            model = self._to_model(task)
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_domain(model)
    
    def update(self, task: Task) -> Task:
        with self.session_factory() as session:
            model = session.query(TaskModel).filter(TaskModel.id == task.id).first()
            if model is None:
                raise TaskNotFoundError(f"Task with id {task.id} not found.")
            model.title = task.title
            model.description = task.description
            model.deadline = task.deadline
            model.is_completed = task.is_completed
            model.completed_at = task.completed_at
            model.notified_24h = task.notified_24h
            model.notified_1h = task.notified_1h
            model.notified_overdue = task.notified_overdue
            model.created_at = task.created_at
            model.updated_at = task.updated_at
            
            session.commit()
            session.refresh(model)
            return self._to_domain(model)
        
    def list_all(self) -> list[Task]:
        with self.session_factory() as session:
            models = session.query(TaskModel).all()
            return [self._to_domain(model) for model in models]
    
    def delete(self, task_id: int) -> None:
        with self.session_factory() as session:
            model = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if model is None:
                raise TaskNotFoundError(f"Task with id {task_id} not found.")
            session.delete(model)
            session.commit()
    
    
