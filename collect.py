from trade.collector.Collector import Collector
from datetime import datetime, timezone
from trade.utils.interval import Interval
from trade.constants import SPOT_BTC


collector = Collector('binance', 1, dropIfExists=False, connector={"host": "10.23.38.185"})
collector.auto_fill(SPOT_BTC,
                    Interval.DAY_1,
                    datetime(2024, 6, 1, tzinfo=timezone.utc))
