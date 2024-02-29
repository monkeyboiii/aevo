DROP TABLE IF EXISTS candles;

CREATE TABLE IF NOT EXISTS candles (
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
) TIMESTAMP(startTime) PARTITION BY MONTH;

INSERT INTO
  candles (
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
  ('BTCUSDT',
  28923.63000000,
  29031.34000000,
  28690.17000000,
  28995.13000000,
  2311.81144500,
  1609459200000, -- TODO: lacking 3 digits
  1609462799999, -- above
  '1h',
  66768830.34010008,
  58389,
  1215.35923800,
  35103542.78288276
  )

  SELECT * FROM candles;