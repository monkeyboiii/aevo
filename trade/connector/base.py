from abc import ABC, abstractmethod
from typing import Mapping, Optional, Sequence, Tuple
from datetime import datetime
from ..constants import Candle
from ..utils.inst import Tradable
from ..utils.interval import Interval


class BaseConnector(ABC):

    conn = None  # connection

    @abstractmethod
    def connect(self, **kwargs):
        '''connect to a new db instance'''
        pass

    @abstractmethod
    def latest_candle(self,
                      inst: Tradable,
                      interval: Optional[Interval] = None,
                      all: bool = False) -> Mapping[Interval, Optional[Candle]]:
        '''located the latest in db'''
        pass

    @abstractmethod
    def retrieve_candles(self,
                         inst: Tradable,
                         interval: Interval,
                         period: Tuple[datetime, datetime]) -> Sequence[Candle]:
        '''retrieve (bulk) candles from db'''
        pass

    @abstractmethod
    def store_candles(self, candles: Sequence[Candle]):
        '''stores (bulk) candles to db'''
        pass

    @abstractmethod
    def find_gaps(self,
                  inst: Tradable,
                  interval: Interval,
                  period: Tuple[datetime, datetime]) -> Sequence[Tuple[datetime, datetime]]:
        '''gap-island problem, passes in & returns all inclusive ranges'''
        pass
