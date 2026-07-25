from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ddl_reminder.infrastructure.models import Base


def create_sqlite_engine(database_url: str = "sqlite:///tasks.db"):
    return create_engine(database_url)

def create_session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database(engine):
    Base.metadata.create_all(engine)

