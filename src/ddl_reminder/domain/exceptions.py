class TaskError(Exception):
    """任务领域错误的基础异常。"""


class TaskNotFoundError(TaskError):
    """任务未找到。"""


class InvalidTaskTitleError(TaskError):
    """任务标题无效。"""


class InvalidDeadlineError(TaskError):
    """任务截止日期无效。"""
