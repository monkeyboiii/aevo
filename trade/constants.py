from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Literal, Union
from .utils.interval import Interval
from .utils.inst import Asset, Spot, Future


COLLECTOR_START_TIME_TIMESTAMP = datetime(2021, 1, 1, tzinfo=timezone.utc)


INTERVAL_SELECTED = {
    'XS': Interval.MINUTE_15,
    'S': Interval.HOUR_1,
    'M': Interval.HOUR_4,
    'L': Interval.DAY_1,
    'XL': Interval.WEEK_1,
}


SPOT_BTC = Spot(Asset.BTC, Asset.USDT)
SPOT_ETH = Spot(Asset.ETH, Asset.USDT)
PERP_BTC = Future(Asset.ETH, Asset.USDT, isPerp=True)


INSTRUMENT_SELECTED = [SPOT_BTC, SPOT_ETH]


class Candle(BaseModel):
    '''Local db compatible candlestick format'''

    inst: str
    open_: float
    high: float
    close: float
    low: float
    volume: float

    startTimeInMicroSec: int
    endTimeInMicroSec: int

    interval: str

    quoteVolume: Union[float, Literal['NULL']] = 'NULL'
    trades: Union[int, Literal['NULL']] = 'NULL'
    takerBuyBaseVolume: Union[float, Literal['NULL']] = 'NULL'
    takerBuyQuoteVolume: Union[float, Literal['NULL']] = 'NULL'

    @property
    def abstract(self) -> str:
        return f'[{self.inst}] opens on [{datetime.fromtimestamp(self.startTimeInMicroSec / 1_000_000).isoformat()}] at [{self.open_}]'
