## Build LangChain Diagram

### Instructions:
1. **File**: Use the `langchain-diagram.md` file as the destination for the diagram.
2. **Source**: Refer to the **SOTA** folder in `sota-summary.pdf` to build the LangChain diagram.
3. **Diagram Format**: The diagram should include key components such as:
   - **Input Processing**
   - **Language Models (LLM)** such as OpenAI
   - **Chains** for sequential operations
   - **Agents** for dynamic decision-making
   - **Memory** for conversational context
   - **Tools** (databases, APIs, etc.)
   - Any **external APIs or databases** mentioned in the SOTA summary.
   
### Example Structure:


```mermaid
---
config:
  look: classic
  theme: base
  layout: dagre
---
graph TD
User["User<br>(Provides input)"] -->|Interacts with| LangChain
subgraph LangChain
InputProcessing["Input Processing<br>(Validates and preprocesses input)"]
LLM["Language Model<br>(e.g., OpenAI)"]
Chains["Chains<br>(Sequence of operations)"]
Agents["Agents<br>(Dynamic decision-making)"]
Memory["Memory<br>(Stores conversation state)"]
Tools["Tools<br>(External services, data retrievers)"]
end

InputProcessing -->|Sends request| LLM
LLM -->|Returns response| InputProcessing
InputProcessing -->|Feeds into| Chains
Chains -->|Handles tasks| Agents
Agents -->|Uses state| Memory
Agents -->|Interacts with| Tools
Tools -->|Uses| DataQueryEngine["DataQueryEngine<br>(Dynamic SQL Library)"]
Tools -->|Queries data| Database["Database<br>(e.g., QuestDB)"]
Tools -->|Interacts with| ExternalAPI["External API<br>(e.g., OpenAI API)"]
Tools -->|Processes Data Stream| DataStream["Data Stream<br>(Real-time data processing)"]
Tools -->|Handles Machine Learning| ML["Machine Learning<br>(Python-based processing)"]
LangChain -->|Returns results| User
```


### Developed Structure:

This diagram outlines a multi-tiered architecture that begins with user interaction through a classic frontend managed by Nginx. User requests are routed to various services such as the AI Agent UI, VSCode, Grafana, and QuestDB. 

The AI workflow involves an AI Agent processing user inputs with language models, chaining operations through agents that maintain memory and use various tools. These tools, in turn, interact with backend and frontend services like VSCode, QuestDB, Grafana, data streams, and machine learning components. 

Additional interactions ensure continuous updates, data storage, and security management via Certbot handling SSL through Nginx, showcasing a comprehensive system integration from user input to sophisticated AI and backend processing.


```mermaid
---
config:
  look: classic
  theme: base
  layout: dagre
---


graph TD
  %% User and Frontend Layer
  subgraph User_Interaction["User Interaction"]
    User["User<br>(Provides input)"] -->|Accesses via| Nginx["Nginx<br>(Port 80/443)"]
  end

  subgraph Frontend["Frontend Layer"]
    Nginx -->|Routes to| AgentUI["AI Agent UI<br>(Port 5000)"]
    Nginx -->|Routes to| VSCode["VSCode<br>(Port 8080)"]
    Nginx -->|Routes to| Grafana["Grafana<br>(Port 3000)"]
    Nginx -->|Routes to| QuestDB["QuestDB<br>(Ports 9000, 8812, 9009)"]
  end

  %% AI & LangChain Workflow
  subgraph AI_Workflow["Core of the AI Agent Lab"]
    AgentUI -->|Sends requests| AIAgent["AI Agent<br>(Port 5001)"]
    AIAgent -->|Returns response| AgentUI
    AIAgent -->|Uses| InputProcessing["Input Processing"]
    InputProcessing -->|Processes with| LLM["Language Model<br>(OpenAI API)"]
    LLM -->|Feeds into| Chains["Chains"]
    Chains -->|Executes| Agents["Agents"]
    Agents -->|Maintains| Memory["Memory"]
    Agents -->|Uses| Tools["Tools"]
  end

  %% Backend Services
  subgraph Backend["Backend Services"]
  
    Tools -->|Executes code on| VSCode
    VSCode -->|Provides data to| QuestDB
    Tools -->|Generates and Executes Queries| QuestDB
    Tools -->|Updates| Grafana
    Tools -->|Manages Queries in| DataQueryEngine["DataQueryEngine"]
    Tools -->|Processes| DataStream["Data Stream"]
    Tools -->|Runs| ML["Machine Learning"]
  end

  %% Additional Interactions and Security
  AIAgent -->|Stores data in| QuestDB
  AIAgent -->|Updates| Grafana
  AIAgent -->|Triggers| VSCode
  QuestDB -->|Provides data to| Grafana

  Certbot["Certbot"] -->|Manages SSL| Nginx
```


### Partial Structure with QuestDB
This updated diagram retains only the components and connections related to QuestDB 

```mermaid
---
config:
  look: classic
  theme: base
  layout: dagre
---

graph TD
  %% User and Frontend Layer
  subgraph User_Interaction["User Interaction"]
    User["User<br>(Provides input)"] -->|Accesses via| Nginx["Nginx<br>(Port 80/443)"]
  end

  subgraph Frontend["Frontend Layer"]
    Nginx -->|Routes to| AgentUI["AI Agent UI<br>(Port 5000)"]
    Nginx -->|Routes to| QuestDB["QuestDB<br>(Ports 9000, 8812, 9009)"]
  end

  %% AI & LangChain Workflow
  subgraph AI_Workflow["Core of the AI Agent Lab"]
    AgentUI -->|Sends requests| AIAgent["AI Agent<br>(Port 5001)"]
    AIAgent -->|Returns response| AgentUI
    AIAgent -->|Uses| InputProcessing["Input Processing"]
    InputProcessing -->|Processes with| LLM["Language Model<br>(OpenAI API)"]
    LLM -->|Feeds into| Chains["Chains"]
    Chains -->|Executes| Agents["Agents"]
    Agents -->|Maintains| Memory["Memory"]
    Agents -->|Uses| Tools["Tools"]
  end

  %% Backend Services
  subgraph Backend["Backend Services"]
    Tools -->|Manages Queries in| DataQueryEngine["DataQueryEngine"]
    Tools -->|Generates and Executes Queries| QuestDB
    Tools -->|Processes| DataStream["Data Stream"]
    Tools -->|Runs| ML["Machine Learning"]
  end

  %% Additional Interactions and Security
  AIAgent -->|Stores data in| QuestDB
  Certbot["Certbot"] -->|Manages SSL| Nginx
```



### Partial Structure with Grafana
This updated diagram retains only the components and connections related to Grafana


```mermaid
---
config:
  look: classic
  theme: base
  layout: dagre
---

graph TD
  %% User and Frontend Layer
  subgraph User_Interaction["User Interaction"]
    User["User<br>(Provides input)"] -->|Accesses via| Nginx["Nginx<br>(Port 80/443)"]
  end

  subgraph Frontend["Frontend Layer"]
    Nginx -->|Routes to| AgentUI["AI Agent UI<br>(Port 5000)"]
    Nginx -->|Routes to| Grafana["Grafana<br>(Port 3000)"]
  end

  %% AI & LangChain Workflow
  subgraph AI_Workflow["Core of the AI Agent Lab"]
    AgentUI -->|Sends requests| AIAgent["AI Agent<br>(Port 5001)"]
    AIAgent -->|Returns response| AgentUI
    AIAgent -->|Uses| InputProcessing["Input Processing"]
    InputProcessing -->|Processes with| LLM["Language Model<br>(OpenAI API)"]
    LLM -->|Feeds into| Chains["Chains"]
    Chains -->|Executes| Agents["Agents"]
    Agents -->|Maintains| Memory["Memory"]
    Agents -->|Uses| Tools["Tools"]
  end

  %% Backend Services
  subgraph Backend["Backend Services"]
    Tools -->|Manages Queries in| DataQueryEngine["DataQueryEngine"]
    Tools -->|Updates| Grafana
    Tools -->|Processes| DataStream["Data Stream"]
    Tools -->|Runs| ML["Machine Learning"]
  end

  %% Additional Interactions and Security
  AIAgent -->|Updates| Grafana

  Certbot["Certbot"] -->|Manages SSL| Nginx

```



### Partial Structure with Vscode

This updated diagram retains only the components and connections related to Vscode

```mermaid
---
config:
  look: classic
  theme: base
  layout: dagre
---

graph TD
  %% User and Frontend Layer
  subgraph User_Interaction["User Interaction"]
    User["User<br>(Provides input)"] -->|Accesses via| Nginx["Nginx<br>(Port 80/443)"]
  end

  subgraph Frontend["Frontend Layer"]
    Nginx -->|Routes to| AgentUI["AI Agent UI<br>(Port 5000)"]
    Nginx -->|Routes to| VSCode["VSCode<br>(Port 8080)"]
  end

  %% AI & LangChain Workflow
  subgraph AI_Workflow["Core of the AI Agent Lab"]
    AgentUI -->|Sends requests| AIAgent["AI Agent<br>(Port 5001)"]
    AIAgent -->|Returns response| AgentUI
    AIAgent -->|Uses| InputProcessing["Input Processing"]
    InputProcessing -->|Processes with| LLM["Language Model<br>(OpenAI API)"]
    LLM -->|Feeds into| Chains["Chains"]
    Chains -->|Executes| Agents["Agents"]
    Agents -->|Maintains| Memory["Memory"]
    Agents -->|Uses| Tools["Tools"]
  end

  %% Backend Services
  subgraph Backend["Backend Services"]
    Tools -->|Manages Queries in| DataQueryEngine["DataQueryEngine"]
    Tools -->|Executes code on| VSCode
    Tools -->|Processes| DataStream["Data Stream"]
    Tools -->|Runs| ML["Machine Learning"]
  end

  %% Additional Interactions and Security
  AIAgent -->|Triggers| VSCode

  Certbot["Certbot"] -->|Manages SSL| Nginx


```





### Core of the AI Agent Lab

The Core of the AI Agent Lab is meticulously designed with a modular architecture, ensuring flexibility and ease of integration with external services such as QuestDB, Grafana, and VSCode with minimal modifications. At its heart lies the AI Agent, which processes incoming requests through the Input Processing module. This module leverages a Language Model (e.g., OpenAI API) to interpret and generate meaningful responses. 

The processed data then flows into Chains, which orchestrate the workflow by directing tasks to specialized Agents. These Agents are responsible for executing specific functions, maintaining contextual Memory, and utilizing various Tools.

The modularity of the core is achieved by abstracting the interactions with external services into the Tools component. This design allows each tool—whether it be QuestDB for robust data management, Grafana for dynamic data visualization, or VSCode for code execution and development—to be integrated independently. By encapsulating the logic for each external service within its respective tool module, the core remains untouched when adding or updating integrations. 

This separation of concerns not only simplifies the development and maintenance process but also enhances the scalability of the AI Agent Lab. Consequently, developers can extend the system's capabilities by incorporating new tools or modifying existing ones without altering the foundational AI workflows, thereby fostering a versatile and resilient AI ecosystem.



```mermaid
---
config:
  look: classic
  theme: base
  layout: dagre
---

graph TD
  subgraph AI_Workflow["Core of the AI Agent Lab"]
    AIAgent["AI Agent<br>(Port 5001)<br>Central Controller"] 
      -->|Uses| InputProcessing["Input Processing<br>(Prepares and routes input)"]
    InputProcessing -->|Processes with| LLM["Language Model<br>(OpenAI API)"]
    LLM -->|Feeds into| Chains["Chains<br>(Defines workflow sequences)"]
    Chains -->|Executes| Agents["Agents<br>(Task executors)"]
    Agents -->|Maintains| Memory["Memory<br>(Context storage)"]
    Agents -->|Uses| Tools["Tools<br>(Extended capabilities)"]
  end

```