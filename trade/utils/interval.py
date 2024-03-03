from enum import Enum
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


class Interval(Enum):
    SECOND_1 = "1s"

    MINUTE_1 = "1m"
    MINUTE_3 = "3m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"

    HOUR_1 = '1h'
    HOUR_2 = '2h'
    HOUR_4 = '4h'
    HOUR_6 = '6h'
    HOUR_8 = '8h'
    HOUR_12 = '12h'

    DAY_1 = '1d'
    DAY_3 = '3d'

    WEEK_1 = '1w'

    MONTH_1 = '1M'


_INTERVAL_TO_RELATIVEDELTA = {
    Interval.SECOND_1: {"seconds": 1},

    Interval.MINUTE_1: {"minutes": 1},
    Interval.MINUTE_3: {"minutes": 3},
    Interval.MINUTE_5: {"minutes": 5},
    Interval.MINUTE_15: {"minutes": 15},
    Interval.MINUTE_30: {"minutes": 30},

    Interval.HOUR_1: {"hours": 1},
    Interval.HOUR_2: {"hours": 2},
    Interval.HOUR_4: {"hours": 4},
    Interval.HOUR_6: {"hours": 6},
    Interval.HOUR_8: {"hours": 8},
    Interval.HOUR_12: {"hours": 12},

    Interval.DAY_1: {"days": 1},
    Interval.DAY_3: {"days": 3},

    Interval.WEEK_1: {"weeks": 1},

    Interval.MONTH_1: {"months": 1},
}


def nextIntervalDatetime(dt: datetime, interval: Interval, count: int = 1) -> datetime:
    args = _INTERVAL_TO_RELATIVEDELTA[interval].copy()
    args = {k: v * count for k, v in args.items()}
    return dt + relativedelta(**args)


def microSecToDatetime(microSec: int) -> datetime:
    return datetime.fromtimestamp(int(microSec / 1_000_000)).replace(tzinfo=timezone.utc)


def msToDatetime(ms: int) -> datetime:
    return datetime.fromtimestamp(int(ms / 1_000)).replace(tzinfo=timezone.utc)


def datetimeToMicroSec(dt: datetime) -> int:
    return int(dt.timestamp() * 1_000_000)


def datetimeToMs(dt: datetime) -> int:
    return int(dt.timestamp() * 1_000)


if __name__ == '__main__':
    start = datetime(2024, 1, 31)
    print(nextIntervalDatetime(start, Interval.SECOND_1))
    print(nextIntervalDatetime(start, Interval.MINUTE_1))
    print(nextIntervalDatetime(start, Interval.MINUTE_3))
    print(nextIntervalDatetime(start, Interval.MINUTE_5))
    print(nextIntervalDatetime(start, Interval.MINUTE_15))
    print(nextIntervalDatetime(start, Interval.HOUR_1))
    print(nextIntervalDatetime(start, Interval.HOUR_2))
    print(nextIntervalDatetime(start, Interval.HOUR_4))
    print(nextIntervalDatetime(start, Interval.HOUR_6))
    print(nextIntervalDatetime(start, Interval.HOUR_8))
    print(nextIntervalDatetime(start, Interval.HOUR_12))
    print(nextIntervalDatetime(start, Interval.DAY_1))
    print(nextIntervalDatetime(start, Interval.DAY_3))
    print(nextIntervalDatetime(start, Interval.WEEK_1))
    print(nextIntervalDatetime(start, Interval.MONTH_1))
