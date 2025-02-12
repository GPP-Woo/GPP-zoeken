from datetime import date, datetime
from zoneinfo import ZoneInfo

TIMEZONE_AMS = ZoneInfo("Europe/Amsterdam")


def date_to_datetime(value: date) -> datetime:
    """return the date as datetime from the timezone Europe/Amsterdam"""
    return datetime.combine(value, datetime.min.time(), tzinfo=TIMEZONE_AMS)
