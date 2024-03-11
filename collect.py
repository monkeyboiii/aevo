from trade.collector.Collector import Collector
from datetime import datetime, timezone
from trade.utils.interval import Interval
from trade.constants import SPOT_BTC


collector = Collector('binance', 1, dropIfExists=True)
collector.auto_fill(SPOT_BTC,
                    Interval.HOUR_4,
                    datetime(2024, 3, 1, tzinfo=timezone.utc))
