from trade.collector.Collector import Collector
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from trade.utils.interval import Interval
from trade.constants import SPOT_BTC


now = datetime.now(tz=timezone.utc)
START_TIME = datetime(2024, 3, 3, tzinfo=timezone.utc) - relativedelta(days=5)


collector = Collector('binance', 1, dropIfExists=True)
collector.auto_fill(SPOT_BTC, Interval.DAY_1, START_TIME)