from datetime import date, time

import pytest

from ddl_reminder.domain.deadline_input import parse_deadline


@pytest.mark.parametrize("day,clock", [
    ("2026-02-29", "12:00"), ("2026-04-31", "12:00"),
    ("2026-13-01", "12:00"), ("2026-00-01", "12:00"),
    ("0000-01-01", "00:00"), ("20261119", "12:00"),
    ("2026-11-19", "24:00"), ("2026-11-19", "23:60"),
    ("2026-11-19", "1230"), ("2026-11-19", "12:00:00"),
    ("2026-11-19", "12:00+08:00"), ("2026-11-19", ""),
])
def test_rejects_invalid_calendar_or_noncanonical_input(day, clock):
    with pytest.raises(ValueError):
        parse_deadline(day, clock)


@pytest.mark.parametrize("day,clock", [
    ("2024-02-29", "00:00"), ("2026-12-31", "23:59"),
    ("0001-01-01", "00:00"), ("9999-12-31", "23:59"),
])
def test_accepts_leap_day_and_inclusive_limits(day, clock):
    assert parse_deadline(day, clock) == (date.fromisoformat(day), time.fromisoformat(clock))
