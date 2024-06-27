from .base import BaseClient
from typing import Sequence
from ..utils.candle import Candle
from ..utils.interval import Interval
from ..utils.inst import *


class OKXClient(BaseClient):
    def __init__(self):
        raise NotImplementedError()

    def toLocaleInst(self, inst: Tradable) -> str:
        if type(inst) is Spot:
            return f'{inst.base.value}-{inst.quote.value}'
        elif type(inst) is Future:
            return f'{inst.base.value}-{inst.quote.value}'
        else:
            raise TypeError(f'Tradable type {type(inst)} not supported')

    def getInstList(self, **kwargs):
        raise NotImplementedError()

    def getCandles(self, inst: Tradable, interval: Interval, **kwargs) -> Sequence[Candle]:
        raise NotImplementedError()
