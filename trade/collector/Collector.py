from typing import Optional, Sequence, Union
from loguru import logger
from time import sleep
from datetime import datetime, timezone
from ..client.base import BaseClient
from ..client.Binance import BinanceClient
from ..client.OKX import OKXClient
from ..connector.base import BaseConnector
from ..connector.quest import QuestConnector, Transaction
from ..utils.inst import Tradable
from ..utils.interval import Interval, nextIntervalDatetime, microSecToDatetime, datetimeToMs
from ..utils.sql import *
from ..constants import Candle, COLLECTOR_START_TIME_TIMESTAMP, INTERVAL_SELECTED, INSTRUMENT_SELECTED, SPOT_ETH


EXCHANGES = {
    'binance': BinanceClient,
    'okx': OKXClient,
}
RETRIEVE_SINGLE_LIMIT = 1000
RETRIEVE_SLEEP_TIME = 2


class Collector:
    """ collect candles from exchanges, then store in database """

    retriever: BaseClient
    storage: BaseConnector

    exchange: str
    suffix: int

    def __init__(self,
                 exchange='binance',
                 suffix=0,
                 dropIfExists=False):
        self.exchange = exchange.lower()
        self.suffix = suffix

        if self.exchange not in EXCHANGES.keys():
            raise ValueError(f'exchange {self.exchange} not supported')

        # data source
        self.retriever = EXCHANGES[self.exchange]()

        # time series db
        self.storage = QuestConnector(exchange=exchange, suffix=suffix)

        # table manipulation
        with Transaction(self.storage) as tx:
            if dropIfExists:
                confirm = input('Are you sure to `DROP TABEL candles_{exchange}_{suffix}` [y/N]'.format(
                    exchange=self.exchange,
                    suffix=self.suffix
                ))
                if confirm is not None and confirm.upper() == 'Y':
                    tx.execute(SQL_DROP_CANDLES.format(
                        exchange=self.exchange,
                        suffix=suffix
                    ))
                    logger.critical('Table candles_{exchange}_{suffix} dropped'.format(
                        exchange=self.exchange,
                        suffix=self.suffix
                    ))
                else:
                    logger.warning(f'Drop action canceled')
            tx.execute(SQL_CREATE_CANDLE.format(
                exchange=self.exchange, suffix=self.suffix))

    ################################################################################

    def get_candles(self,
                    inst: Tradable,
                    interval: Interval,
                    start: datetime,
                    end: datetime,
                    storeIfRetrieved: bool = True
                    ) -> Sequence[Candle]:
        ''' get candles from storage or retriever'''
        pass

    def auto_fill(self,
                  inst: Tradable,
                  interval: Interval,
                  start: Optional[datetime] = None,
                  end: Optional[datetime] = None):
        '''fill with candles from start to end'''

        candle = self.storage.latest_candle(inst, interval)[interval]
        emptyDB = candle is None
        fix = not emptyDB  # fix first incomplete candle
        startInDB = COLLECTOR_START_TIME_TIMESTAMP if emptyDB else microSecToDatetime(
            candle.startTimeInMicroSec)

        ptr = max(start, startInDB) if start is not None else startInDB
        end = end if end is not None else datetime.now(timezone.utc)

        while ptr < end:
            try:
                nextPtr = nextIntervalDatetime(
                    ptr, interval, RETRIEVE_SINGLE_LIMIT)

                # DEBUG: what if ptr + 1000 > end

                # retrieve and store
                logger.info(f'retrieve [{interval.value}] {ptr} -> {nextPtr}')
                actual = self._retrieve_and_store(inst,
                                                  interval,
                                                  store=True,
                                                  fix=fix,
                                                  # kwargs
                                                  startTime=datetimeToMs(ptr),
                                                  limit=RETRIEVE_SINGLE_LIMIT)
                logger.debug(f'one round complete [{actual}] filled')

                sleep(RETRIEVE_SLEEP_TIME)

                ptr = nextPtr
                fix = False

            except KeyboardInterrupt:
                logger.info('exit from interrupt')
                break

        logger.info('auto_fill ended')

    def auto_fill_all_interval(self, inst: Tradable, intervals: Optional[Sequence[Interval]]):
        intvs = intervals if intervals is not None else INTERVAL_SELECTED.values()
        for intv in intvs:
            logger.info(f'start filling [{inst}] [{intv.value}]')
            self.auto_fill(inst, intv)

    def auto_fill_all_inst(self, interval: Interval, insts: Optional[Sequence[Tradable]]):
        instruments = insts if insts is not None else INSTRUMENT_SELECTED
        for inst in instruments:
            logger.info(f'start filling [{inst}] [{interval}]')
            self.auto_fill(inst, interval)

    ################################################################################

    def _retrieve_from_db(self,
                          inst: Tradable,
                          interval: Interval) -> Optional[Sequence[Candle]]:
        self.storage.retrieve_candles()
        pass

    def _retrieve_and_store(self,
                            inst: Tradable,
                            interval: Interval,
                            store: bool = True,
                            fix: bool = False,
                            **kwargs) -> Union[int, Sequence[Candle]]:
        # NOTE: kwargs abstraction & sanitization
        candles = self.retriever.getCandles(inst, interval, **kwargs)

        if not store:
            return candles

        self.storage.store_candles(candles, fix)

        return len(candles)


if __name__ == '__main__':
    from dateutil.relativedelta import relativedelta

    collector = Collector('binance', 1)
    collector.auto_fill(SPOT_ETH,
                        Interval.MINUTE_15,
                        datetime.now(tz=timezone.utc) - relativedelta(hours=15))
