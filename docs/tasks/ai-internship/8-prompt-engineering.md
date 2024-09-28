# Prompt Engineering

## Task: Create Optimized Engineering Prompts for Live Market Data in the Database

### Instructions:
1. **File**: Use the `prompt-engineering.md` file to document the optimized prompts you create.
2. **Objective**: Engineer prompts that query **live market data streams** stored in the database, return the response on the **user interface**, and include a **link to the relevant Grafana dashboard** for real-time visualization.

### Key Guidelines for Market Data Prompt Engineering (Live Data):

- **Live Data Streams**: The prompts should be designed to query live, continuously updated market data (e.g., Bitcoin price movements, trading volumes, and technical indicators) from the database.
- **Real-Time Results**: Ensure that the AI Agent provides up-to-date, real-time results on the user interface, reflecting the current state of the market.
- **Grafana Dashboard Link**: Each response must include a link to a **real-time Grafana dashboard**, where users can further explore the live data stream.
- **Optimization**: The prompts should focus on retrieving relevant live data efficiently and ensuring the results are clearly displayed with an active link to the Grafana dashboard for live data visualization.

### Example Prompt Structures for Live Data Streams with Grafana Links:

1. **Moving Average (MA)**:
   - Query live Bitcoin price data and calculate the moving average in real time, with a link to the Grafana dashboard for live monitoring.
   - **Example**: "Query the live Bitcoin price data in the database and calculate the 50-day and 200-day moving averages in real time. Display the results on the UI and include a link to the live Grafana dashboard for moving averages."

2. **Relative Strength Index (RSI)**:
   - Retrieve real-time RSI data from live streams and link to Grafana for visualization.
   - **Example**: "Query live Bitcoin price data from the database, calculate the RSI in real time, and display the results with a link to the live Grafana RSI dashboard."

3. **Volatility Analysis**:
   - Analyze live volatility based on real-time price fluctuations, with a Grafana link for continuous monitoring.
   - **Example**: "Retrieve live Bitcoin price data from the database, analyze volatility in real time, and display the results on the UI with a link to the live Grafana volatility dashboard."

4. **Trading Volume Analysis**:
   - Query live trading volume data and link to a real-time Grafana dashboard for visualization.
   - **Example**: "Query live Bitcoin trading volume data from the database, display the key trends in real time, and include a link to the live Grafana dashboard for trading volume."

5. **Support and Resistance Levels**:
   - Identify live support and resistance levels based on real-time data, with a link to Grafana for ongoing updates.
   - **Example**: "Query live Bitcoin price data from the database, calculate real-time support and resistance levels, display the results, and include a link to the live Grafana dashboard for support/resistance analysis."

### Deliverable:
For each prompt, document the following in the **`prompt-engineering.md`** file:
- **Prompt**: The market data-focused prompt querying live data streams from the database.
- **Objective**: The goal or task the prompt is trying to achieve (e.g., calculating real-time technical indicators, analyzing live trends).
- **Test Results**: Notes on how the AI Agent displayed the live data response on the UI and included a working link to the relevant live Grafana dashboard.
- **Iterations**: List any adjustments made to the prompt and the resulting improvements in the AI’s responses.

### Example Entry:

```markdown
### Prompt: 
"Query the live Bitcoin price data in the database and calculate the 50-day and 200-day moving averages in real time. Display the results on the UI and include a link to the live Grafana dashboard for moving averages."

- **Objective**: To retrieve moving average data from the live data stream in the database and link it to the relevant live Grafana dashboard for real-time monitoring.
- **Test Results**: The initial response included outdated data, not reflecting the live stream.
- **Iteration 1**: Adjusted the prompt to explicitly mention querying live data and updated the link to Grafana's real-time dashboard.
- **Outcome**: The prompt returned accurate, real-time moving average data with a working Grafana link for live monitoring. Optimized.
```

### Creating a Library of Optimized Engineering Prompts for Market Data

To further enhance the financial capabilities of the AI Agent Lab, we can develop a **library of optimized engineering prompts** specifically designed for **market data**. This library will serve as a repository of well-tested prompts that allow the AI Agent to retrieve and analyze financial metrics, such as price movements, technical indicators, and market trends, from the database. By standardizing and organizing these prompts, the library will ensure consistency in querying financial data, allowing the AI Agent to generate highly accurate and actionable insights.

This collection of prompts can be continuously expanded and refined to cover a wide range of market data tasks, such as calculating technical indicators (e.g., Moving Averages, RSI, Bollinger Bands) or generating risk assessments, market forecasts, and trend analyses. Additionally, the prompts will be optimized to query live data streams and link seamlessly with the Grafana dashboards, ensuring real-time data monitoring and analysis. 
