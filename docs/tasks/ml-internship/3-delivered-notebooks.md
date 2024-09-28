# Delivered Python Files and SQL Templates

This document tracks the delivery of **several sets of Python scripts and SQL templates** as part of the internship. Each set consists of:
- A Python script for live data stream processing.
- A Python script for machine learning analysis.
- SQL templates for technical indicators used in the data processing.

Each script and SQL file should meet the following criteria:
- Efficiently handle live data stream processing.
- Apply machine learning models to analyze processed data.
- Use SQL-based queries for technical indicators from the database.
- Be optimized for real-time performance and integration with GPT-3.5 models and the AI Agent Lab.

## File Delivery Checklist

### Python Script Sets

| Set Name                   | Script Name                | Description                                                     | Status    | Date Delivered | Comments/Notes                   |
|----------------------------|----------------------------|-----------------------------------------------------------------|-----------|----------------|----------------------------------|
| Set 1: Data Stream and ML   | `data-stream-processing.py` | Ingests live market data streams, applies SQL-based technical indicators for analysis. | In Progress | N/A            | Handles live data ingestion and SQL query execution for technical analysis. |
|                            | `ml-processing.py`          | Applies machine learning models to analyze processed data from live streams (e.g., regression, clustering, time-series analysis). | In Progress | N/A            | To implement regression and clustering models on SQL query results. |
| Set 2: Additional Models    | (To be defined)             | Further sets will include more specialized scripts for different machine learning models and data processing techniques. | Not Started | N/A            | Future sets will focus on specific models and data sources. |

### SQL Templates for Technical Indicators

| SQL Template   | Description                                               | Status    | Date Delivered | Comments/Notes |
|----------------|-----------------------------------------------------------|-----------|----------------|----------------|
| `sma.sql`      | SQL query for calculating the Simple Moving Average (SMA). | Not Started | N/A            | Will use it in data stream processing. |
| `ema.sql`      | SQL query for calculating the Exponential Moving Average (EMA). | Not Started | N/A            | Will use it in data stream processing. |
| `rsi.sql`      | SQL query for calculating the Relative Strength Index (RSI). | Not Started | N/A            | To be integrated for trend analysis. |
| `macd.sql`     | SQL query for calculating the Moving Average Convergence Divergence (MACD). | Not Started | N/A            | Will be used in data stream and machine learning tasks. |
| `macd.sql`     | SQL query for calculating the Moving Average Convergence Divergence (MACD). | Not Started | N/A            | Will be used in data stream and machine learning tasks. |
## Submission Guidelines

1. Ensure all Python scripts and SQL templates are committed to the designated repository.
2. Each set of scripts and SQL templates should have proper comments and documentation for readability and maintainability.
3. Scripts must be tested with real-time data and SQL queries to ensure they meet performance benchmarks.
4. Update this document with the status of each script and SQL template, and include notes where necessary.

## Notes

- Python script sets should integrate smoothly with the existing AI Agent Lab infrastructure and handle SQL queries for technical indicators.
- SQL templates should be reusable and easily modifiable for additional technical indicators.


