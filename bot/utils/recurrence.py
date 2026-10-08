from __future__ import annotations
from datetime import datetime, timedelta
from typing import List

from bot.database.models import RecurrenceType

MAX_OCCURRENCES = 120


def generate_occurrences(start_at: datetime, recurrence: str, until: datetime | None = None, 
                         max_count: int = MAX_OCCURRENCES) -> List[datetime]:
    """Возвращает список дат начала занятий (включая первое) для серии."""
    if recurrence == RecurrenceType.NONE.value or recurrence is None:
        return [start_at]

    if recurrence == RecurrenceType.DAILY.value:
        step = timedelta(days=1)
    elif recurrence == RecurrenceType.WEEKLY.value:
        step = timedelta(weeks=1)
    elif recurrence == RecurrenceType.MONTHLY.value:
        step = timedelta(days=30)  # упрощение
    else:
        raise ValueError(f"Unknown recurrence: {recurrence}")

    result: List[datetime] = []
    current = start_at
    if until is None:
        until = start_at + step * 11

    while current <= until and len(result) < max_count:
        result.append(current)
        current = current + step
    return result