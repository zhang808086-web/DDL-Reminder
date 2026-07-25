from datetime import date, datetime, time
import pytest
from ddl_reminder.domain.deadline import (
    DeadlineCategory,
    classify_deadline,
    format_remaining_time,
    normalize_deadline,
)
from ddl_reminder.domain.exceptions import InvalidDeadlineError


# --- normalize_deadline ---

def test_normalize_deadline_uses_2359_when_time_is_missing():
    result = normalize_deadline(date(2026, 7, 17))

    assert result == datetime(2026, 7, 17, 23, 59)


def test_normalize_deadline_uses_given_time():
    result = normalize_deadline(date(2026, 7, 17), time(10, 30))

    assert result == datetime(2026, 7, 17, 10, 30)


def test_normalize_deadline_rejects_none_date():
    with pytest.raises(InvalidDeadlineError):
        normalize_deadline(None)


# --- classify_deadline ---

def test_classify_deadline_treats_exact_deadline_as_overdue():
    category, seconds = classify_deadline(
        datetime(2026, 7, 17, 23, 59),
        datetime(2026, 7, 17, 23, 59),
    )

    assert category == DeadlineCategory.OVERDUE
    assert seconds == 0


def test_classify_deadline_treats_exact_one_hour_as_within_one_hour():
    category, seconds = classify_deadline(
        datetime(2026, 7, 18, 0, 59),
        datetime(2026, 7, 17, 23, 59),
    )

    assert category == DeadlineCategory.WITHIN_ONE_HOUR
    assert seconds == 3600


def test_classify_deadline_treats_exact_one_day_as_within_one_day():
    category, seconds = classify_deadline(
        datetime(2026, 7, 18, 23, 59),
        datetime(2026, 7, 17, 23, 59),
    )

    assert category == DeadlineCategory.WITHIN_ONE_DAY
    assert seconds == 86400


def test_classify_deadline_treats_exact_three_days_as_within_three_days():
    category, seconds = classify_deadline(
        datetime(2026, 7, 20, 23, 59),
        datetime(2026, 7, 17, 23, 59),
    )

    assert category == DeadlineCategory.WITHIN_THREE_DAYS
    assert seconds == 259200


def test_classify_deadline_treats_more_than_three_days_as_normal():
    category, seconds = classify_deadline(
        datetime(2026, 7, 21, 23, 59),
        datetime(2026, 7, 17, 23, 59),
    )

    assert category == DeadlineCategory.NORMAL
    assert seconds == 345600


# --- format_remaining_time ---

def test_format_remaining_time_shows_overdue_days():
    dl = datetime(2026, 7, 15, 12, 0)
    now = datetime(2026, 7, 17, 12, 0)

    result = format_remaining_time(dl, now)

    assert result == "已逾期2天"


def test_format_remaining_time_shows_overdue_hours():
    dl = datetime(2026, 7, 17, 9, 0)
    now = datetime(2026, 7, 17, 12, 0)

    result = format_remaining_time(dl, now)

    assert result == "已逾期3小时"


def test_format_remaining_time_shows_zero_hours_when_overdue_less_than_one_hour():
    dl = datetime(2026, 7, 17, 11, 30)
    now = datetime(2026, 7, 17, 12, 0)

    result = format_remaining_time(dl, now)

    assert result == "已逾期0小时"


def test_format_remaining_time_shows_remaining_days():
    dl = datetime(2026, 7, 19, 12, 0)
    now = datetime(2026, 7, 17, 12, 0)

    result = format_remaining_time(dl, now)

    assert result == "剩余2天"


def test_format_remaining_time_shows_remaining_hours():
    dl = datetime(2026, 7, 17, 14, 42)
    now = datetime(2026, 7, 17, 12, 0)

    result = format_remaining_time(dl, now)

    assert result == "剩余2小时"


def test_format_remaining_time_shows_zero_minutes_when_less_than_one_minute_left():
    dl = datetime(2026, 7, 17, 12, 0, 30)
    now = datetime(2026, 7, 17, 12, 0)

    result = format_remaining_time(dl, now)

    assert result == "剩余0分钟"
