from dataclasses import dataclass
from datetime import date, time

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    
)

@dataclass
class TaskFormData:
    title: str
    description: str
    deadline_date: date
    deadline_time: time | None
    
class TaskDialog(QDialog):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.setWindowTitle("新建任务")
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        form_layout.addRow("标题", self.title_edit)
        
        self.description_edit = QTextEdit()
        form_layout.addRow("描述", self.description_edit)
        
        self.deadline_date_edit = QDateEdit()
        self.deadline_date_edit.setCalendarPopup(True)
        self.deadline_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("日期", self.deadline_date_edit)
        
        self.has_time_checkbox = QCheckBox("设置具体时间")
        form_layout.addRow("", self.has_time_checkbox)
        
        self.deadline_time_edit = QTimeEdit()
        self.deadline_time_edit.setTime(QTime(23,59))
        self.deadline_time_edit.setEnabled(False)
        form_layout.addRow("时间", self.deadline_time_edit)
        
        self.has_time_checkbox.toggled.connect(self.deadline_time_edit.setEnabled)
        layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        
    def get_data(self) -> TaskFormData:
        qdate = self.deadline_date_edit.date()
        deadline_date = date(qdate.year(), qdate.month(), qdate.day())
        
        if self.has_time_checkbox.isChecked():
            qtime = self.deadline_time_edit.time()
            deadline_time = time(qtime.hour(), qtime.minute(), qtime.second())
            
        else: 
            deadline_time = None
            
        return TaskFormData(
            title = self.title_edit.text(),
            description = self.description_edit.toPlainText(),
            deadline_date = deadline_date,
            deadline_time = deadline_time
        )
        
        
        
        
    
    
        