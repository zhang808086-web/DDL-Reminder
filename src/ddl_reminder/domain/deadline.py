from datetime import date, datetime, time
from enum import Enum

from ddl_reminder.domain.exceptions import InvalidDeadlineError


class DeadlineCategory(Enum):
    OVERDUE = "overdue"
    WITHIN_ONE_HOUR = "within_one_hour"
    WITHIN_ONE_DAY = "within_one_day"
    WITHIN_THREE_DAYS = "within_three_days"
    NORMAL = "normal"


def classify_deadline(deadline: datetime, now: datetime) -> tuple[DeadlineCategory, int]:
    """计算deadline相对now的紧迫程度和剩余秒数"""
    seconds_diff = (deadline - now).total_seconds()

    if seconds_diff <= 0:
        return DeadlineCategory.OVERDUE, int(seconds_diff)
    if seconds_diff <= 3600:
        return DeadlineCategory.WITHIN_ONE_HOUR, int(seconds_diff)
    if seconds_diff <= 86400:
        return DeadlineCategory.WITHIN_ONE_DAY, int(seconds_diff)

    if seconds_diff <= 259200:
        return DeadlineCategory.WITHIN_THREE_DAYS, int(seconds_diff)

    return DeadlineCategory.NORMAL, int(seconds_diff)


def normalize_deadline(deadline_date: date, deadline_time: time | None = None) -> datetime:
    """将日期和时间组合成datetime对象"""
    if deadline_date is None:
        raise InvalidDeadlineError("Deadline cannot be None")
    if deadline_time is None:
        return datetime.combine(deadline_date, time(23, 59))
    return datetime.combine(deadline_date, deadline_time)


def format_remaining_time(deadline: datetime, now: datetime) -> str:
    """格式化剩余时间"""
    seconds_diff = int((deadline - now).total_seconds())
    if seconds_diff <= 0:
        seconds_diff = abs(seconds_diff)
        days, remainder = divmod(seconds_diff, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days != 0:
            return f"已逾期{days}天"
        if days == 0 and hours != 0:
            return f"已逾期{hours}小时"
        else:
            return f"已逾期0小时"

    elif seconds_diff > 0:
        days, remainder = divmod(seconds_diff, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days != 0:
            return f"剩余{days}天"
        if days == 0 and hours != 0:
            return f"剩余{hours}小时"
        if days == 0 and hours == 0 and minutes != 0:
            return f"剩余{minutes}分钟"
        return f"剩余{minutes}分钟"
