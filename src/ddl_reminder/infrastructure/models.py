from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime,Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(15), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable = False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notified_1h: Mapped[bool] = mapped_column(Boolean, default=False, nullable = False)
    notified_24h: Mapped[bool] = mapped_column(Boolean, default=False, nullable = False)
    notified_overdue: Mapped[bool] = mapped_column(Boolean, default=False, nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False)
