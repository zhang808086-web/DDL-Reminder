from PySide6.QtCore import QLockFile, QStandardPaths

class SingleInstanceLock:
    def __init__(self, app_name: str = "ddl-reminder") -> None:
        temp_dir = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
        self._lock_file = QLockFile(f"{temp_dir}/{app_name}.lock")
        
    def try_lock(self) -> bool:
        self._lock_file.setStaleLockTime(0)
        return self._lock_file.tryLock(100)
    
    def unlock(self) -> None:
        self._lock_file.unlock()
    