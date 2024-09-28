SELECT timestamp time,
       symbol,
       price,
       avg(price)
       OVER (PARTITION BY symbol
             ORDER BY timestamp
             RANGE 1 MINUTE PRECEDING ) moving_average_1m,
FROM trades
WHERE $__timeFilter(timestamp)
AND   symbol = '$Pairs'
