## Task: Create Optimized Engineering Prompts for Financial Data in the Database

### Instructions:
1. **File**: Use the `prompt-engineering.md` file to document the optimized prompts you create.
2. **Objective**: Engineer prompts that return the most optimized and relevant responses from the **financial data stored in the database**, particularly focusing on cryptocurrency data like **Bitcoin**.

### Key Guidelines for Financial Data Prompt Engineering:

- **Database Focus**: Ensure that all prompts are designed to query and retrieve relevant financial data directly from the database. The AI should process and analyze the data stored in the database, such as historical price movements, trading volumes, and other key financial metrics.
- **Clarity**: Make sure the prompts are clear and specify the relevant data in the database that needs to be queried (e.g., time ranges, specific data fields).
- **Optimization**: Ensure that the prompts are efficient and retrieve precise, actionable financial insights from the database, avoiding redundant or irrelevant data.
- **Iterative Testing**: After testing the prompts, refine them to improve the accuracy and efficiency of the database queries and results.

### Example Prompt Structures for Database-Focused Financial Data:

1. **Historical Price Query**:
   - Retrieve historical price data for specific timeframes.
   - **Example**: "Query the Bitcoin price data stored in the database for the last 7 days and summarize the key price changes."

2. **Trading Volume Analysis**:
   - Query trading volume data to provide insights on market activity.
   - **Example**: "Retrieve Bitcoin trading volume from the database for the past 30 days and analyze the most significant changes in trading activity."

3. **Price Comparison**:
   - Compare the price of Bitcoin at two specific points in time using the data in the database.
   - **Example**: "Compare the Bitcoin price stored in the database from January 1st to March 1st and explain the key factors that led to any price changes."

4. **Volatility Analysis**:
   - Query data on price fluctuations to assess volatility over a given period.
   - **Example**: "Query the Bitcoin price fluctuations for the past month in the database and assess the volatility during this period."

5. **Correlation with External Events**:
   - Analyze the relationship between external events and Bitcoin price data stored in the database.
   - **Example**: "Retrieve Bitcoin price data for the day after the recent Federal Reserve announcement and analyze how the price was affected."

### Deliverable:
For each prompt, document the following in the **`prompt-engineering.md`** file:
- **Prompt**: The financial data-focused prompt querying the database.
- **Objective**: The goal or task the prompt is trying to achieve (e.g., retrieving historical price data, analyzing trading volumes).
- **Test Results**: Notes on how the AI responded to the prompt, including the accuracy and optimization of the data retrieved from the database.
- **Iterations**: List any adjustments made to the prompt and the resulting improvements in the AI’s responses.

### Example Entry:

```markdown
### Prompt: 
"Query the Bitcoin price data stored in the database for the last 7 days and summarize the key price changes."

- **Objective**: To retrieve and summarize Bitcoin price changes from the database for the past 7 days.
- **Test Results**: The initial response included irrelevant data outside the specified time range.
- **Iteration 1**: Adjusted prompt to: "Only query the Bitcoin price data from the last 7 days stored in the database."
- **Outcome**: The response was refined to include only the relevant data. Optimized.
