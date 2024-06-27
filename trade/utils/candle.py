from pydantic import BaseModel
from typing import Literal, Union
from .interval import microSecToDatetime


class Candle(BaseModel):
    '''Local db-compatible candlestick format'''

    inst:                   str
    open_:                  float
    high:                   float
    close:                  float
    low:                    float
    volume:                 float

    startTimeInMicroSec:    int     # NOTE: utc timestamp
    endTimeInMicroSec:      int     # NOTE: utc timestamp

    interval:               str

    # optional
    quoteVolume:            Union[float, Literal['NULL']] = 'NULL'
    trades:                 Union[int,   Literal['NULL']] = 'NULL'
    takerBuyBaseVolume:     Union[float, Literal['NULL']] = 'NULL'
    takerBuyQuoteVolume:    Union[float, Literal['NULL']] = 'NULL'

    @property
    def abstract(self) -> str:
        return f'[{self.inst}] opens on [{microSecToDatetime(self.startTimeInMicroSec).isoformat()}] at [{self.open_}]'
