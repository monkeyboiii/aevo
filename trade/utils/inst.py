from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum
from datetime import datetime


_SETTLEMENT_FORMAT = '%y%m%d'


def _getSettlementDate(dt: datetime) -> str:
    '''e.g. 2024-03-02 -> 240302'''
    return dt.date().strftime(_SETTLEMENT_FORMAT)


class Asset(Enum):
    BTC: str = "BTC"
    ETH: str = "ETH"
    USDT: str = "USDT"
    USDC: str = "USDC"


class Tradable(ABC):
    def __init__(self, base: Asset, quote: Asset):
        self.base = base
        self.quote = quote

    def base(self) -> Asset:
        return self.base

    def quote(self) -> Asset:
        return self.quote

    @property
    @abstractmethod
    def symbol(self) -> str:
        '''local symbol in the database'''
        pass

    @staticmethod
    def fromString(s: str):
        bp = s.split('-')
        base = bp[0]
        quote = bp[1]
        if len(bp) == 3:
            settlement = bp[2]
            if settlement == 'PERP':
                return Future(Asset(base), Asset(quote))
            else:
                return Future(Asset(base), Asset(quote), settlement=datetime.strptime(_SETTLEMENT_FORMAT))
        return Spot(Asset(base), Asset(quote))


class Spot(Tradable):
    @property
    def symbol(self) -> str:
        return f'{self.base.value}-{self.quote.value}'


class Future(Tradable):
    def __init__(self, base: Asset, quote: Asset, settlement: Optional[datetime] = None, isPerp: bool = True):
        super().__init__(base, quote)
        self.isPerp = isPerp
        self.settle = None if self.isPerp else settlement

    @property
    def symbol(self) -> str:
        return f'{self.base.upper()}-{self.quote.upper()}-{'PERP' if self.isPerp else _getSettlementDate()}'
