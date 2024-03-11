from typing import Mapping, Optional, Sequence, Tuple
import psycopg2 as pg
from loguru import logger
from datetime import datetime
from .base import BaseConnector
from ..utils.inst import Tradable
from ..utils.interval import Interval, datetimeToMicroSec, microSecToDatetime
from ..utils.sql import SQL_INSERT_CANDLE, SQL_MOST_RECENT_CANDLE, SQL_UPDATE_CANDLE, SQL_SELECT_CANDLE
from ..constants import Candle, INTERVAL_SELECTED


DEFAULT_EXCHANGE = 'binance'
DEFAULT_SUFFIX = 88


def datetimeToMicroSecStr(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

class Transaction:
    cursor = None

    def __init__(self, connector: BaseConnector) -> None:
        self.outerConn = connector.conn

    def __enter__(self):
        self.cursor = self.outerConn.cursor()
        return self.cursor

    def __exit__(self, *exc):
        self.outerConn.commit()
        self.cursor.close()


class QuestConnector(BaseConnector):

    exchange: str
    suffix: int

    def __init__(self, **kwargs) -> None:
        self.conn = pg.connect(user=kwargs.get('user', 'admin'),
                               password=kwargs.get('password', 'quest'),
                               host=kwargs.get('host', '127.0.0.1'),
                               port=kwargs.get('port', '8812'),
                               database=kwargs.get('database', 'qdb'))
        self.exchange = kwargs.get('exchange', DEFAULT_EXCHANGE)
        self.suffix = kwargs.get('suffix', DEFAULT_SUFFIX)

    def connect(self, **kwargs):
        '''reconnect to a new db'''
        self.conn = pg.connect(**kwargs)

    def latest_candle(self,
                      inst: Tradable,
                      interval: Optional[Interval] = None,
                      all: bool = False) -> Mapping[Interval, Optional[Candle]]:
        if interval is not None:
            ret = {interval: None}
        elif not all:
            ret = {intv: None for intv in INTERVAL_SELECTED.values()}
        else:
            ret = {intv: None for intv in Interval}

        list_ = ', '.join(map(lambda k: f"'{k.value}'", ret.keys()))
        intervalClause = f' AND interval in ({list_})' if not all else ''
        sql = SQL_MOST_RECENT_CANDLE.format(exchange=self.exchange,
                                            suffix=self.suffix,
                                            inst=inst.symbol,
                                            intervalClause=intervalClause)

        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()

            for candle in results:
                (inst, open_, high, low, close, volume,
                    startTime, endTime, interval_,
                    quoteVolume, trades,
                    takerBuyBaseVolume, takerBuyQuoteVolume) = candle

                ret[Interval(interval_)] = Candle(
                    inst=inst,

                    open_=open_,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,

                    startTimeInMicroSec=datetimeToMicroSec(startTime),
                    endTimeInMicroSec=datetimeToMicroSec(endTime),

                    interval=interval_,

                    quoteVolume=quoteVolume,
                    trades=trades,
                    takerBuyBaseVolume=takerBuyBaseVolume,
                    takerBuyQuoteVolume=takerBuyQuoteVolume
                )

        return ret

    def retrieve_candles(self,
                         inst: Tradable,
                         interval: Interval,
                         period: Tuple[datetime]) -> Sequence[Candle]:
        ret = []
        sql = SQL_SELECT_CANDLE.format(
            exchange=self.exchange,
            suffix=self.suffix,
            inst=inst.symbol,
            interval=interval.value,
            startTimeStr=datetimeToMicroSecStr(period[0]),
            endTimeStr=datetimeToMicroSecStr(period[1])
        )

        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetch_all()

            for candle in results:
                (inst, open_, high, low, close, volume,
                    startTime, endTime, interval_,
                    quoteVolume, trades,
                    takerBuyBaseVolume, takerBuyQuoteVolume) = candle

                ret.append(Candle(
                    inst=inst,

                    open_=open_,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,

                    startTimeInMicroSec=datetimeToMicroSec(startTime),
                    endTimeInMicroSec=datetimeToMicroSec(endTime),

                    interval=interval_,

                    quoteVolume=quoteVolume,
                    trades=trades,
                    takerBuyBaseVolume=takerBuyBaseVolume,
                    takerBuyQuoteVolume=takerBuyQuoteVolume
                ))

        return ret

    def store_candles(self, candles: Sequence[Candle], fix: bool = False):
        '''may fix first incomplete candle'''

        with self.conn.cursor() as cursor:
            for i, candle in enumerate(candles):
                # REVIEW: check existence first?
                if fix and i == 0:
                    cursor.execute(SQL_UPDATE_CANDLE.format(
                        exchange=self.exchange,
                        suffix=self.suffix,
                        **candle.dict()
                    ))
                    logger.debug('first entry updated [{inst} {interval}] [{time}]'.format(
                        inst=candle.inst,
                        interval=candle.interval,
                        time=microSecToDatetime(
                            candle.startTimeInMicroSec).isoformat()
                    ))
                    continue

                cursor.execute(SQL_INSERT_CANDLE.format(
                    exchange=self.exchange,
                    suffix=self.suffix,
                    **candle.dict()
                ))

            self.conn.commit()

    def find_gaps(self,
                  inst: Tradable,
                  interval: Interval,
                  period: Tuple[datetime]) -> Sequence[Tuple[datetime]]:
        raise NotImplementedError()
