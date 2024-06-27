from typing import Sequence
from .base import BaseClient
from binance.spot import Spot as SpotClient
from ..utils.candle import Candle
from ..utils.interval import Interval
from ..utils.inst import Tradable, Spot, Future


PARAMETER_MAPPING = {

}


def toCandle(inst: Tradable, interval: Interval, candle) -> Candle:
    (startTimeInMs, open_, high, low, close, volume, endTimeInMs,
        quoteVolume, trades, takerBuyBaseVolume, takerBuyQuoteVolume, _) = candle

    return Candle(
        inst=inst.symbol,

        open_=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,

        startTimeInMicroSec=startTimeInMs * 1000,
        endTimeInMicroSec=endTimeInMs * 1000,

        interval=interval.value,

        quoteVolume=quoteVolume,
        trades=trades,
        takerBuyBaseVolume=takerBuyBaseVolume,
        takerBuyQuoteVolume=takerBuyQuoteVolume
    )


class BinanceClient(BaseClient):
    def __init__(self):
        # NOTE: improve to include futures
        self.spot_client = SpotClient()

    def toLocaleInst(self, inst: Tradable) -> str:
        if type(inst) is Spot:
            return f'{inst.base.value}{inst.quote.value}'
        elif type(inst) is Future:
            # TODO: investigate the correct form
            return f'{inst.base.value}{inst.quote.value}'
        else:
            raise TypeError(f'Tradable type {type(inst)} not supported')

    def getInstList(self, **kwargs):
        raise NotImplementedError()

    def getCandles(self, inst: Tradable, interval: Interval, **kwargs) -> Sequence[Candle]:
        """ 
            kwargs includes startTime, endTime, limit.
            startTime first, endTime second, then try to satisfy limit
        """
        localeInst = self.toLocaleInst(inst)
        intv = interval.value

        candles = self.spot_client.klines(localeInst, intv, **kwargs)
        return list(map(lambda c: toCandle(inst, interval, c), candles))


if __name__ == '__main__':
    from loguru import logger
    from datetime import datetime
    from ..constants import SPOT_BTC
    from ..utils.interval import datetimeToMs
    
    # DEBUG: timestamp vs datetime
    client = BinanceClient()
    candles = client.getCandles(SPOT_BTC, Interval.SECOND_1, **{
        # no timezone info since we only need the timestamp
        "startTime": datetimeToMs(datetime(2024, 3, 1)),
        "endTime": datetimeToMs(datetime(2024, 3, 2)),
        "limit": 1001,
    })

    # for i, candle in enumerate(candles):
    #     logger.debug(f'{candle.abstract} {i}')
    logger.debug(f'{len(candles)} total candles')
    logger.debug(candles[0].abstract)
    logger.debug(candles[-1].abstract)
