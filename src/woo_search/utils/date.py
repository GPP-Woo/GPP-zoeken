from datetime import date, datetime
from zoneinfo import ZoneInfo

TIMEZONE_AMS = ZoneInfo("Europe/Amsterdam")


def date_to_datetime(value: date, timezone: ZoneInfo = TIMEZONE_AMS) -> datetime:
    """return the date as datetime of specific timezone, default timezone is Europe/Amsterdam"""
    return datetime.combine(value, datetime.min.time(), tzinfo=timezone)
