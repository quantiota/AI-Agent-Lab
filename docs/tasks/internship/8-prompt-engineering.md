## Task: Create Optimized Engineering Prompts for Financial Data in the Database

### Instructions:
1. **File**: Use the `prompt-engineering.md` file to document the optimized prompts you create.
2. **Objective**: Engineer prompts that return the most optimized and relevant responses from the **financial data stored in the database**, particularly focusing on cryptocurrency data like **Bitcoin** and incorporating **technical indicators** for analysis.

### Key Guidelines for Financial Data Prompt Engineering:

- **Database Focus**: Ensure all prompts are designed to query and retrieve financial data directly from the database, including price movements, trading volumes, and technical indicators.
- **Technical Indicators**: Integrate common technical indicators such as Moving Averages (MA), Relative Strength Index (RSI), Bollinger Bands, and more to enhance financial analysis.
- **Optimization**: Ensure that the prompts are efficient and return relevant, actionable financial insights from the database, avoiding unnecessary or redundant data.
- **Iterative Testing**: Refine and optimize the prompts after testing, focusing on accurate technical analysis using the data retrieved from the database.

### Example Prompt Structures for Database-Focused Financial Data and Technical Indicators:

1. **Moving Average (MA)**:
   - Query the database for Bitcoin price data and calculate a moving average for a specified period.
   - **Example**: "Retrieve Bitcoin price data from the database and calculate the 50-day and 200-day moving averages. Analyze if the price is above or below these moving averages."

2. **Relative Strength Index (RSI)**:
   - Calculate the RSI to assess whether Bitcoin is overbought or oversold.
   - **Example**: "Query Bitcoin price data from the past 14 days in the database and calculate the RSI. Indicate whether Bitcoin is in an overbought or oversold condition based on the RSI value."

3. **Bollinger Bands**:
   - Use Bollinger Bands to analyze Bitcoin price volatility.
   - **Example**: "Retrieve Bitcoin price data for the past 20 days from the database and calculate Bollinger Bands. Analyze whether the price is trading near the upper or lower band."

4. **Exponential Moving Average (EMA)**:
   - Use EMA to analyze recent price trends.
   - **Example**: "Query Bitcoin price data for the last 30 days in the database and calculate the 12-day and 26-day exponential moving averages. Analyze whether the short-term trend is bullish or bearish."

5. **MACD (Moving Average Convergence Divergence)**:
   - Analyze price momentum using MACD.
   - **Example**: "Retrieve Bitcoin price data for the past 60 days from the database and calculate the MACD. Indicate if there are any bullish or bearish crossovers."

6. **Support and Resistance Levels**:
   - Identify key support and resistance levels based on historical data.
   - **Example**: "Query the Bitcoin price data stored in the database for the past 6 months and calculate key support and resistance levels based on previous highs and lows."

### Deliverable:
For each prompt, document the following in the **`prompt-engineering.md`** file:
- **Prompt**: The financial data-focused prompt querying the database.
- **Objective**: The goal or task the prompt is trying to achieve (e.g., calculating technical indicators, identifying trends).
- **Test Results**: Notes on how the AI responded to the prompt, including the accuracy and optimization of the technical analysis based on the data retrieved from the database.
- **Iterations**: List any adjustments made to the prompt and the resulting improvements in the AI’s responses.

### Example Entry:

```markdown
### Prompt: 
"Retrieve Bitcoin price data from the database and calculate the 50-day and 200-day moving averages. Analyze if the price is above or below these moving averages."

- **Objective**: To calculate and analyze the 50-day and 200-day moving averages for Bitcoin using data stored in the database.
- **Test Results**: The initial response did not accurately retrieve the correct moving averages.
- **Iteration 1**: Adjusted prompt to specify "only the last 50 and 200 days" for better accuracy in the query.
- **Outcome**: The prompt now returns accurate moving average values. Optimized.
