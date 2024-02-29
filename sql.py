SQL_CREATE_CANDLE = '''
CREATE TABLE
    IF NOT EXISTS candles (
        inst SYMBOL,
        open DOUBLE,
        low DOUBLE,
        high DOUBLE,
        close DOUBLE,
        startTime TIMESTAMP,
        endTime TIMESTAMP,
        interval STRING
    ) TIMESTAMP(startTime)
PARTITION BY
    MONTH;
'''


