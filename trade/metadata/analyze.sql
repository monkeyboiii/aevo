-- lag 1 and 2
SELECT
    inst,
    open,
    startTime,
    FIRST_VALUE (open) OVER (
        PARTITION BY
            inst,
            interval
        ORDER BY
            startTime row BETWEEN 1 PRECEDING AND 1  PRECEDING
    ) AS price_lag_1,
    FIRST_VALUE (open) OVER (
        PARTITION BY
            inst,
            interval
        ORDER BY
            startTime row BETWEEN 2 PRECEDING AND 2  PRECEDING
    ) AS price_lag_2
FROM
    candles_binance_1
WHERE
    inst = 'ETH-USDT';

-- choppiness
WITH CandlestickData AS (
    SELECT
        startTime,
        high,
        low,
        close
    FROM
        candles_binance_1
    WHERE inst = 'ETH-USDT' 
    ORDER BY startTime
) , ATRData AS (
    SELECT
        startTime,
        TRANGE(high, low, close) AS true_range
    FROM
        CandlestickData
    ORDER BY
        startTime
), AverageATR AS (
    SELECT
        AVG(true_range) AS avg_atr
    FROM
        ATRData
) SELECT
    *
FROM
    AverageATR;