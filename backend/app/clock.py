"""Calendar-date bounds for user-entered dates.

Browsers submit the athlete's local calendar date, while the server (UTC in containers)
has its own. Between local midnight and UTC midnight an athlete east of UTC is already
on the next date, so "today" must not be rejected as a future date. UTC+14 is the
furthest civil time-zone offset in use.
"""

from datetime import date, datetime, timedelta, timezone

MAX_UTC_OFFSET = timedelta(hours=14)


def latest_user_date(now: datetime | None = None) -> date:
    """Latest calendar date that is 'today' somewhere; later dates are in the future."""
    return ((now or datetime.now(timezone.utc)).astimezone(timezone.utc) + MAX_UTC_OFFSET).date()
