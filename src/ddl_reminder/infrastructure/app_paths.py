from __future__ import annotations

import os
from pathlib import Path


APP_DIR_NAME = "DDL-Reminder"

def get_app_data_dir() -> Path:
    app_data = os.environ.get("APPDATA")
    
    if app_data is None:
        base_dir = Path.home()
    else:
        base_dir = Path(app_data)
    
    app_dir = base_dir / APP_DIR_NAME
    app_dir.mkdir(parents = True, exist_ok = True)
    return app_dir
    
def get_database_path() -> Path:
    return get_app_data_dir() / "tasks.db"
    

def get_log_path() -> Path:
    return get_app_data_dir() / "ddl-reminder.log"