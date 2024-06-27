from datetime import datetime, timezone
from .utils.interval import Interval
from .utils.inst import Spot, Future
from .utils.asset import Asset


COLLECTOR_START_TIME_TIMESTAMP = datetime(2021, 1, 1, tzinfo=timezone.utc)


INTERVAL_SELECTED = {
    'XS':           Interval.MINUTE_15,
    'S':            Interval.HOUR_1,
    'M':            Interval.HOUR_4,
    'L':            Interval.DAY_1,
    'XL':           Interval.WEEK_1,
}


SPOT_BTC =                  Spot  (Asset.BTC, Asset.USDT)
SPOT_ETH =                  Spot  (Asset.ETH, Asset.USDT)
PERP_BTC_USDT =             Future(Asset.BTC, Asset.USDT, isPerp=True)
PERP_ETH_USDT =             Future(Asset.ETH, Asset.USDT, isPerp=True)
FUTURE_241201_BTC_USDT =    Future(Asset.BTC, Asset.USDT, settlement='241201')
FUTURE_241201_ETH_USDT =    Future(Asset.ETH, Asset.USDT, settlement='241201')


INSTRUMENT_SELECTED = [SPOT_BTC, SPOT_ETH]
