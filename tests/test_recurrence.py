from datetime import datetime

import pytest

from bot.utils.recurrence import generate_occurrences


def test_none_returns_single():
    dt = datetime(2025, 1, 1, 10, 0)
    assert generate_occurrences(dt, "none") == [dt]


def test_weekly_with_until():
    start = datetime(2025, 1, 1, 10, 0)
    until = datetime(2025, 1, 22, 10, 0)
    dates = generate_occurrences(start, "weekly", until)
    assert len(dates) == 4
    assert dates[0] == start
    assert dates[-1] == until


def test_daily_default_count():
    start = datetime(2025, 1, 1, 10, 0)
    dates = generate_occurrences(start, "daily")
    assert len(dates) == 12


def test_monthly():
    start = datetime(2025, 1, 1, 10, 0)
    until = datetime(2025, 4, 1, 10, 0)
    dates = generate_occurrences(start, "monthly", until)
    assert len(dates) == 4


def test_unknown_recurrence():
    with pytest.raises(ValueError):
        generate_occurrences(datetime.utcnow(), "yearly")


def test_max_count_cap():
    start = datetime(2025, 1, 1)
    until = datetime(2030, 1, 1)
    dates = generate_occurrences(start, "daily", until, max_count=10)
    assert len(dates) == 10