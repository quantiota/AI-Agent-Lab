# TA-Library: SQL Query Technical Indicators

## Overview
The `ta-library` contains a collection of SQL queries to compute technical indicators used in  market data analysis. These queries are optimized for use with [QuestDB](https://questdb.io/), a high-performance time-series database. The results of these queries can be visualized using [Grafana](https://grafana.com/) to track live market data streams.



### How to Use

**Visualize in Grafana**: Once you have QuestDB connected to Grafana, you can visualize these indicators in a custom dashboard by running the queries as data sources.



## SQL Query Technical Indicators
The following technical indicators are included:

1. Simple Moving Average (SMA)
Calculates the average price over a specified number of periods.

```sql
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
```