from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ddl_reminder.infrastructure.models import Base


def create_sqlite_engine(database_url: str = "sqlite:///tasks.db"):
    # Allow the desktop app and stdio MCP process to share the user's SQLite DB.
    options = {"connect_args": {"timeout": 15}} if database_url.startswith("sqlite:") else {}
    return create_engine(database_url, **options)

def create_session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database(engine):
    Base.metadata.create_all(engine)

