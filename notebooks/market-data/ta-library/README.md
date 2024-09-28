# TA-Library: SQL Query Technical Indicators

## Overview
The `ta-library` contains a collection of SQL queries to compute technical indicators used in  market data analysis. These queries are optimized for use with [QuestDB](https://questdb.io/), a high-performance time-series database. The results of these queries can be visualized using [Grafana](https://grafana.com/) to track live market data streams.


### Database Schema

Your financial data should be stored in QuestDB using the following schema:
```sql
CREATE TABLE market_data (
    ts TIMESTAMP,
    price DOUBLE,
    volume DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE
) TIMESTAMP(ts);
```

#### How to Use

1. **Run Queries**: Execute the SQL queries from this library on your QuestDB instance to calculate technical indicators.

2. **Visualize in Grafana**: Once you have QuestDB connected to Grafana, you can visualize these indicators in a custom dashboard by running the queries as data sources.



### SQL Query Technical Indicators
The following technical indicators are included:

1. Simple Moving Average (SMA)
Calculates the average price over a specified number of periods.

```sql
SELECT ts, AVG(price) OVER (ORDER BY ts ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS sma
FROM market_data;
```