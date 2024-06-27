--
-- SQL_DROP_CANDLES
DROP TABLE IF EXISTS candles_binance_1;

--
-- SQL_CREATE_CANDLE
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

--
-- SQL_INSERT_CANDLE
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

--
-- SQL_UPDATE_CANDLE
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

--
-- SQL_MOST_RECENT_CANDLE
SELECT
  *
from
  candles_binance_1
WHERE
  inst = 'BTC-USDT'
  AND interval in ('1h', '4h') LATEST ON startTime
PARTITION BY
  inst,
  interval;

-- 
-- SQL_SELECT_CANDLE
SELECT
  *
FROM
  candles_binance_1
WHERE
  inst = 'ETH-USDT'
  AND interval = '1h'
  AND startTime BETWEEN '2024-03-01T00:00:00' AND '2024-03-02T00:00:00';

--
-- SQL_FIND_GAP
/* Still needs to consider 
 * 1. if first period is before the actual startTime in db
 * 2. to substitute args with parameters
 * 3. coordinate utc storing
 */
WITH
  candles_period AS (
    SELECT
      startTime,
      cast(startTime as DOUBLE) as startTimeDouble
    FROM
      candles_binance_1
    WHERE
      inst = 'BTC-USDT'
      AND interval = '4h'
      AND startTime BETWEEN dateadd ('h', -4, '2024-03-01T00:00:00') AND '2024-03-08T00:00:00'
  ),
  candles_window AS (
    SELECT
      startTime,
      FIRST_VALUE (startTimeDouble) OVER (
        ORDER BY
          startTime ROWS BETWEEN 1 PRECEDING
          AND CURRRENT ROW EXCLUDE CURRENT ROW
      ) as prevStartTimeDouble
    FROM
      candles_period
  ),
  candles_gap AS (
    SELECT
      startTime,
      dateadd ('h', -4, startTime) as idealPrevStartTime,
      cast(prevStartTimeDouble as TIMESTAMP) as actualPrevStartTime
  )
SELECT
  startTime,
  prevTime
FROM
  candles_gap
WHERE
  idealPrevStartTime <> actualPrevStartTime;

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