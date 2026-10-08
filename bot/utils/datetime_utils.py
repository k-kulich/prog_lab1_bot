from datetime import datetime, timezone


def utcnow() -> datetime:
    """Naive UTC — так удобнее хранить в SQLite и сравнивать."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_user_datetime(text: str, fmt: str = "%d.%m.%Y %H:%M") -> datetime:
    """Парсит пользовательскую строку. Возвращает naive datetime (в UTC)."""
    dt = datetime.strptime(text.strip(), fmt)
    return dt 