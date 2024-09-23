## AI Agent and AI Agent UI Prototype Definition (Natural Language Focus)

### Objective:
The goal is to develop a foundational AI Agent and AI Agent UI prototype where users interact **exclusively through natural language**. The backend, powered by **LangChain**, handles all interactions with external services such as **QuestDB**, **Grafana**, **Code-Server**, and **OpenAI** via their APIs. The prototype will abstract away all technical details, allowing users to ask questions and issue commands in plain text, while the AI Agent translates those requests into the necessary backend operations.

### AI Agent Prototype (Backend)

1. **Interaction with OpenAI (GPT-3.5)**:
   - The AI agent uses **GPT-3.5** to process user requests and understand the intent behind the natural language input.
   - The AI agent identifies whether the user query requires data from QuestDB, visualizations from Grafana, or actions in Code-Server, based on the context.

2. **LangChain’s Tool Management**:
   - **LangChain** will orchestrate the flow of API requests. Depending on the task (data retrieval, visualization, script execution), it will determine the necessary tools to fulfill the user’s request.
   - For example, LangChain will decide whether to retrieve data from QuestDB, call the Grafana API for visualization, or interact with Code-Server to run a script.

3. **QuestDB Integration (SQL Queries Abstracted)**:
   - When the user asks a data-related question (e.g., "What was the average Bitcoin price last week?"), GPT-3.5 translates the natural language input into an appropriate **SQL query**.
   - The **SQLDatabaseChain module** in LangChain interacts with QuestDB by generating the query and executing it behind the scenes. The user is unaware of the SQL query, seeing only the result in plain text or as a summary.
   - For example, QuestDB might return the average price, which GPT-3.5 will summarize as: "The average Bitcoin price last week was $27,500."

4. **Grafana Integration (Visualization)**:
   - If the user requests a visualization (e.g., "Show me the price trend for Bitcoin last week"), **LangChain** will call the **Grafana API** to generate a visual representation of the data.
   - Instead of displaying the raw data, the user will be given a link or an embedded chart from Grafana that displays the result visually.

5. **Code-Server Interaction (File/Script Automation)**:
   - The AI agent can also interact with **Code-Server** to automate tasks such as running scripts or managing files based on user commands.
   - For example, a user might ask: "Run the data processing script for market data," and the AI agent will trigger the appropriate action in Code-Server without exposing the technical steps to the user.

### AI Agent UI Prototype (Frontend)

1. **Natural Language Interface**:
   - The UI will provide a **text input box** where users can interact with the AI agent through natural language.
   - The interface will be clean and simple, focusing on allowing users to input queries like:
     - "What is the latest stock price for Bitcoin?"
     - "Show me a chart of Bitcoin prices over the last week."
     - "Run the script to process market data."
   - The AI Agent processes these requests and provides results without requiring the user to know any technical details.

2. **Task Automation**:
   - The AI agent will automate backend tasks based on natural language requests, such as:
     - **Fetching data** from QuestDB.
     - **Generating visualizations** through Grafana.
     - **Running scripts** in Code-Server.
   - Users will only see the results (e.g., a summary from GPT-3.5 or a link to a Grafana dashboard).

3. **Quick Links and Feedback**:
   - The UI will offer **quick links** for users to navigate to detailed views in **QuestDB** or **Grafana**, if they need to explore the data further.
   - The system will also display feedback like "Data retrieved successfully" or "Script executed" to confirm task completion.

4. **No Display of Raw Data**:
   - The user interface will not display raw SQL queries, database outputs, or other technical details. Instead, all interactions will be in **natural language**, and results will be returned as **summaries** or **visualizations** as requested by the user.

### Foundation for Future Development:
This prototype serves as the base for more complex future features. The architecture will remain modular, allowing new services to be added easily without altering the fundamental design. The focus will always remain on **natural language interaction** to abstract the technical complexity from the user.

### Key Features:
- **Natural Language Processing**: The AI




