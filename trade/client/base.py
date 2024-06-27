from abc import ABC, abstractmethod
from typing import Optional, Sequence
from datetime import datetime
from ..utils.asset import Asset
from ..utils.candle import Candle
from ..utils.interval import Interval
from ..utils.inst import Tradable


class BaseClient(ABC):
    # @abstractmethod
    # def fromLocaleBaseQuote(self, base: Asset, quote: Asset, settlement: Optional[datetime], isPerp: bool = False) -> Tradable:
    #     pass

    @abstractmethod
    def toLocaleInst(self, inst: Tradable) -> str:
        pass

    @abstractmethod
    def getInstList(self, **kwargs):
        pass

    @abstractmethod
    def getCandles(self, inst: Tradable, interval: Interval, **kwargs) -> Sequence[Candle]:
        pass
