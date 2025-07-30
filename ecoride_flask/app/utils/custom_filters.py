import locale
from datetime import datetime

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")


def fr_date(value):
    if not value:
        return ""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime("%d %B - %H:%Mhs")
