from loguru import logger
import psycopg2 as pg
from time import sleep
import sys
import signal
from typing import Mapping, Optional, Any, Sequence, Union
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from ..client.Base import BaseClient
from ..client.Binance import BinanceClient
from ..client.OKX import OKXClient
from ..utils.inst import Tradable, Spot, Asset
from ..utils.interval import Interval, nextIntervalDatetime, microSecToDatetime, datetimeToMicroSec
from ..utils.sql import *
from ..constants import COLLECTOR_START_TIME_TIMESTAMP, INTERVAL_SELECTED, INSTRUMENT_SELECTED, Candle

EXCHANGES = {
    'binance': BinanceClient,
    # TODO: support more
    'okx': OKXClient,
}
RETRIEVE_SINGLE_LIMIT = 1000
RETRIEVE_SLEEP_TIME = 2


class Collector:

    retriever: BaseClient
    storage: Any

    def __init__(self, exchange='binance', suffix=0, dropIfExists=False):
        self.exchange = exchange.lower()
        self.suffix = suffix
        if self.exchange not in EXCHANGES.keys():
            raise ValueError(f'exchange {self.exchange} not supported')

        # data source
        self.retriever = EXCHANGES[self.exchange]()

        # time series db
        self.storage = pg.connect(user="admin",
                                  password="quest",
                                  host="127.0.0.1",
                                  port="8812",
                                  database="qdb")
        cursor = self.storage.cursor()
        if dropIfExists:
            confirm = input(f'Are you sure to `DROP TABEL candles_{self.exchange}_{self.suffix}` [y/N]')
            if confirm is not None and confirm.upper() == 'Y':
                cursor.execute(SQL_DROP_CANDLES.format(exchange=self.exchange, suffix=suffix))
                logger.critical(f'Table candles_{self.exchange}_{self.suffix} dropped')
            else:
                logger.warning(f'Drop action canceled')
        cursor.execute(SQL_CREATE_CANDLE.format(exchange=self.exchange, suffix=self.suffix))
        self.storage.commit()

    def __del__(self):
        if self.storage:
            self.storage.close()

    ################################################################################
    # public fns
    ################################################################################

    def latest_candle(self, inst: Tradable, interval: Interval) -> Optional[Candle]:
        return self._latest_candle(inst, interval)[interval]

    def auto_fill(self, inst: Tradable, interval: Interval, start: Optional[datetime] = None, end: Optional[datetime] = None):
        '''fill with candles from start to end'''

        candle = self._latest_candle(inst, interval)[interval]
        emptyDB = candle is None
        fixFirst = not emptyDB
        startInDB = COLLECTOR_START_TIME_TIMESTAMP if emptyDB else microSecToDatetime(candle.startTimeInMicroSec)
        if start is not None and not emptyDB:
            ptr = max(start, startInDB)
        else:
            ptr = start
        end = end if end is not None else datetime.now(timezone.utc)
        logger.debug(f'[{inst.symbol} {interval.value}] {start.isoformat()} -> {end.isoformat()}')
        
        while ptr < end:
            try:
                nextPtr = nextIntervalDatetime(ptr, interval, RETRIEVE_SINGLE_LIMIT)
                
                # retrieve and store
                logger.info(f'retrieve [{interval.value}] {ptr} -> {nextPtr}')
                actual = self._retrieve_and_store(inst, interval, fixFirst=fixFirst, startTime=int(ptr.timestamp() * 1_000) ,limit=RETRIEVE_SINGLE_LIMIT)
                logger.debug(f'one round complete [{actual}] filled')
                
                sleep(RETRIEVE_SLEEP_TIME)
                
                ptr = nextPtr
                fixFirst = False

            except KeyboardInterrupt:
                logger.info('exit from interrupt')
                break
        
        logger.info('auto_fill ended')

    def auto_fill_all_interval(self, inst: Tradable):
        for intv in INTERVAL_SELECTED.values():
            logger.info(f'start filling [{inst}] [{intv.value}]')
            self.auto_fill(inst, intv)

    def auto_fill_all_inst(self, interval: Interval):
        for inst in INSTRUMENT_SELECTED:
            logger.info(f'start filling [{inst}] [{interval}]')
            self.auto_fill(inst, interval)

    def auto_fix_gap(self, inst: Tradable, interval: Interval, start: Optional[datetime] = None, end: Optional[datetime] = None):
        '''will fill up the gap from start to end'''
        raise NotImplementedError()

    ################################################################################
    # internal fns
    ################################################################################

    def _latest_candle(self, inst: Tradable, interval: Optional[Interval] = None, allIntervals=False) -> Mapping[Interval, Optional[Candle]]:
        '''in DB'''

        if interval is not None:
            ret = {interval: None}
        elif not allIntervals:
            ret = {intv: None for intv in INTERVAL_SELECTED.values()}
        else:
            ret = {intv: None for intv in Interval}

        list_ = ', '.join(map(lambda k: f"'{k.value}'", ret.keys()))
        intervalClause = f" AND interval in ({list_})" if not allIntervals else ''
        sql = SQL_MOST_RECENT_CANDLE.format(exchange=self.exchange, suffix=self.suffix, inst=inst.symbol, intervalClause=intervalClause)

        cursor = self.storage.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()

        for candle in results:
            inst, open_, high, low, close, volume, startTime, endTime, interval_, quoteVolume, trades, takerBuyBaseVolume, takerBuyQuoteVolume = candle
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

        cursor.close()
        return ret

    def _retrieve_and_store(self, inst: Tradable, interval: Interval, store: bool = True, fixFirst: bool = False, **kwargs) -> Union[int, Sequence[Candle]]:
        # NOTE: kwargs abstraction & sanitization
        candles = self.retriever.getCandles(inst, interval, **kwargs)
        
        if not store:
            return candles

        cursor = self.storage.cursor()
        for i, candle in enumerate(candles):
            if fixFirst and i == 0:
                cursor.execute(SQL_UPDATE_CANDLE.format(
                    exchange=self.exchange,
                    suffix=self.suffix,
                    **candle.dict()    
                ))
                logger.debug(f'first entry updated [{inst.symbol}] [{interval.value}] [{microSecToDatetime(candle.startTimeInMicroSec).isoformat()}]')
                continue
            cursor.execute(SQL_INSERT_CANDLE.format(
                exchange=self.exchange,
                suffix=self.suffix,
                **candle.dict()
            ))

        self.storage.commit()
        cursor.close()
        
        return len(candles)


if __name__ == '__main__':
    logger.debug('from __main__')
    
    collector = Collector('binance', 1)
    inst = Spot(Asset.ETH, Asset.USDT)
    candle = collector.latest_candle(inst, Interval.HOUR_1)
    logger.info(f'{'No abstract' if candle is None else candle.abstract}')

    collector.auto_fill(inst, Interval.HOUR_1, datetime.now(tz=timezone.utc) - relativedelta(hours=15))

