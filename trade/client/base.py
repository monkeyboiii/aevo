from abc import ABC, abstractmethod
from typing import Optional, Sequence
from datetime import datetime
from trade.constants import Candle
from ..utils.interval import Interval
from ..utils.inst import Asset, Tradable


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
