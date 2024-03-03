from .Base import BaseClient
from typing import Sequence
from datetime import datetime
from ..constants import Candle
from ..utils.interval import Interval
from ..utils.inst import *
from binance.spot import Spot as SpotClient


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

    def _toCandle(self, inst: Tradable, interval: Interval, candle) -> Candle:
        startTimeInMs, open_, high, low, close, volume, endTimeInMs, quoteVolume, trades, takerBuyBaseVolume, takerBuyQuoteVolume, _ = candle

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

    def getCandles(self, inst: Tradable, interval: Interval, **kwargs) -> Sequence[Candle]:
        localeInst = self.toLocaleInst(inst)
        intv = interval.value

        candles = self.spot_client.klines(localeInst, intv, **kwargs)
        return list(map(lambda c: self._toCandle(inst, interval, c), candles))
