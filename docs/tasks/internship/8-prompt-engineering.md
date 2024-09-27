## Task: Create Optimized Engineering Prompts for Financial Data in the Database

### Instructions:
1. **File**: Use the `prompt-engineering.md` file to document the optimized prompts you create.
2. **Objective**: Engineer prompts that query the **financial data stored in the database**, and return the response on the **user interface** along with a **link to the relevant Grafana dashboard** for visualization.

### Key Guidelines for Financial Data Prompt Engineering:

- **Database Queries**: All prompts should be designed to query relevant financial data stored in the database, such as Bitcoin price movements, technical indicators, and trading volumes.
- **User Interface**: The AI Agent will return the response on the user interface, so prompts must be clear and structured to provide the user with concise, actionable insights.
- **Grafana Dashboard Links**: For each response, include a link to the relevant Grafana dashboard that visualizes the queried data. This will allow users to further explore the data.
- **Optimization**: Ensure that prompts retrieve precise, relevant data from the database efficiently, and the results are clearly displayed on the user interface.

### Example Prompt Structures for Database-Focused Financial Data with Grafana Links:

1. **Moving Average (MA)**:
   - Query Bitcoin price data and calculate the moving average with a link to the Grafana dashboard for further visualization.
   - **Example**: "Query the Bitcoin price data stored in the database and calculate the 50-day and 200-day moving averages. Display the results on the UI and include a link to the Grafana dashboard for moving averages."

2. **Relative Strength Index (RSI)**:
   - Retrieve RSI data and provide a link to Grafana for visualizing the RSI trend.
   - **Example**: "Query Bitcoin price data from the last 14 days in the database, calculate the RSI, and display the results on the UI with a link to the Grafana RSI dashboard."

3. **Volatility Analysis**:
   - Analyze volatility based on price fluctuations and link to Grafana's volatility dashboard.
   - **Example**: "Retrieve Bitcoin price data for the past month from the database, analyze volatility, and provide a link to the Grafana dashboard showing price volatility."

4. **Trading Volume Analysis**:
   - Query trading volume data and link to a Grafana chart displaying volume trends.
   - **Example**: "Query Bitcoin trading volume for the past 30 days from the database, display the key trends on the UI, and include a link to the Grafana dashboard for trading volume."

5. **Support and Resistance Levels**:
   - Identify key support and resistance levels with a link to the Grafana dashboard.
   - **Example**: "Query Bitcoin price data from the last 6 months stored in the database, calculate support and resistance levels, display the results, and include a link to the Grafana dashboard for further exploration."

### Deliverable:
For each prompt, document the following in the **`prompt-engineering.md`** file:
- **Prompt**: The financial data-focused prompt querying the database.
- **Objective**: The goal or task the prompt is trying to achieve (e.g., calculating technical indicators, identifying trends).
- **Test Results**: Notes on how the AI Agent displayed the response on the UI and included the link to the relevant Grafana dashboard.
- **Iterations**: List any adjustments made to the prompt and the resulting improvements in the AI’s responses.

### Example Entry:

```markdown
### Prompt: 
"Query the Bitcoin price data stored in the database and calculate the 50-day and 200-day moving averages. Display the results on the UI and include a link to the Grafana dashboard for moving averages."

- **Objective**: To retrieve moving average data from the database and link it to the relevant Grafana dashboard for visualization.
- **Test Results**: The initial response did not display the Grafana link.
- **Iteration 1**: Adjusted the prompt to explicitly mention including the link to Grafana for moving averages.
- **Outcome**: The response included the correct moving average data and a working Grafana dashboard link. Optimized.
