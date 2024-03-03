DROP TABLE IF EXISTS candles_binance_1;

CREATE TABLE
  IF NOT EXISTS candles_binance_1 (
    -- most necessary
    inst SYMBOL,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume DOUBLE,
    startTime TIMESTAMP,
    endTime TIMESTAMP,
    -- calculated
    interval STRING,
    -- nullable
    quoteVolume DOUBLE,
    trades INT,
    takerBuyBaseVolume DOUBLE,
    takerBuyQuoteVolume DOUBLE
  ) TIMESTAMP(startTime)
PARTITION BY
  MONTH;

INSERT INTO
  candles_binance_1 (
    -- most necessary
    inst,
    open,
    high,
    low,
    close,
    volume,
    startTime,
    endTime,
    -- calculated
    interval,
    -- nullable
    quoteVolume,
    trades,
    takerBuyBaseVolume,
    takerBuyQuoteVolume
  )
VALUES
  (
    'BTC-USDT',
    28923.63000000,
    29031.34000000,
    28690.17000000,
    28995.13000000,
    2311.81144500,
    1609459200000 * 1000,
    1609462799999 * 1000,
    '1h',
    66768830.34010008,
    58389,
    1215.35923800,
    35103542.78288276
  );

UPDATE candles_binance_1
SET
  open = 30000.63000000,
  low = 20000.63000000,
  high = 40000.63000000,
  close = 32000.63000000,
  volume = 1234,
  endTime = 1609462799999 * 1000,
  quoteVolume = 123,
  trades = 456,
  takerBuyBaseVolume = 123,
  takerBuyQuoteVolume = 123
WHERE
  inst = 'BTC-USDT'
  AND interval = '1h'
  AND startTime = 1609459200000 * 1000;

SELECT
  inst,
  startTime,
  interval
from
  candles_binance_1
WHERE
  inst = 'BTC-USDT' LATEST ON startTime
PARTITION BY
  inst,
  interval;

--
-- DEBUG
--
SELECT
  count(*)
FROM
  candles_binance_0;

WITH
  temp AS (
    SELECT DISTINCT
      startTime
    FROM
      candles_binance_0
  )
SELECT
  count(*)
FROM
  temp;