SQL_DROP_CANDLES = "DROP TABLE IF EXISTS candles_{exchange}_{suffix};"


SQL_CREATE_CANDLE = """
CREATE TABLE
  IF NOT EXISTS candles_{exchange}_{suffix} (
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
"""


SQL_INSERT_CANDLE = """
INSERT INTO
  candles_{exchange}_{suffix} (
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
    '{inst}',
    {open_},
    {high},
    {low},
    {close},
    {volume},
    {startTimeInMicroSec},
    {endTimeInMicroSec},
    '{interval}',
    {quoteVolume},
    {trades},
    {takerBuyBaseVolume},
    {takerBuyQuoteVolume}
  );
"""


SQL_UPDATE_CANDLE = """
UPDATE
  candles_{exchange}_{suffix}
SET
  open = {open_},
  low = {low},
  high = {high},
  close = {close},
  volume = {volume},
  endTime = {endTimeInMicroSec},
  quoteVolume = {quoteVolume},
  trades = {trades},
  takerBuyBaseVolume = {takerBuyBaseVolume},
  takerBuyQuoteVolume = {takerBuyQuoteVolume}
WHERE
  inst = '{inst}' AND interval = '{interval}' AND startTime = {startTimeInMicroSec};
"""


SQL_MOST_RECENT_CANDLE = """
SELECT
  *
from
  candles_{exchange}_{suffix}
WHERE
  inst = '{inst}'{intervalClause} LATEST ON startTime
PARTITION BY
  inst,
  interval;
"""


SQL_SELECT_CANDLE = """
SELECT
  *
FROM
  candles_{exchange}_{suffix}
WHERE
  inst = '{inst}'
  AND interval = '{interval}'
  AND startTime BETWEEN '{startTimeStr}' AND '{endTimeStr}';
"""
