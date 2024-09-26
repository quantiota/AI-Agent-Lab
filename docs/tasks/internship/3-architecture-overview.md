

# Architecture Overview

## Architecture Diagram

The following diagram illustrates the architecture of the AI Agent lab:

```mermaid
graph TD
subgraph Docker Services
codeserver["code-server<br>(Port 8080)"]
grafana["Grafana<br>(Port 3000)"]
questdb["QuestDB<br>(Port 9000, 9009, 8812, 9003)"]
aiagentui["AI Agent UI<br>(Port 5000)"]
nginx["Nginx<br>(Port 80, 443)"]
certbot["Certbot"]
aiagent["AI Agent<br><br>"]
end
User["User<br>"]
User -->|Interacts with| nginx
nginx -->|Routes requests| aiagentui
nginx -->|Routes requests| codeserver
nginx -->|Routes requests| grafana
nginx -->|Routes requests| questdb
aiagentui -->|Sends requests| aiagent
aiagent -->|Sends responses| aiagentui
aiagent <-->|Queries/Writes data| questdb
aiagent <-->|Updates dashboards| grafana
aiagent <-->|Executes code| codeserver
grafana -->|Queries data| questdb
certbot -->|Manages SSL Certificates| nginx
OpenAI["OpenAI API"]
aiagent <-->|Sends requests/Receives responses| OpenAI
classDef toDevelop fill:#f9f,stroke:#333,stroke-width:2px;
class aiagent toDevelop;
classDef external fill:#f0f0f0,stroke:#333,stroke-dasharray: 5 5;
class OpenAI external;
```

## Architecture Highlights:
- **AI Agent**: The core AI service that processes user requests from the AI Agent UI. It interacts with various components:
  - **QuestDB**: Queries and writes data for storage and retrieval.
  - **Grafana**: Updates dashboards to visualize data and insights.
  - **code-server**: Executes code and scripts to perform tasks.
  - **OpenAI API**: Communicates with the external API for natural language processing and AI capabilities.

- **AI Agent UI**: A user-friendly interface (Flask-based) that allows users to interact with the AI Agent. It sends user requests to the AI Agent and displays the generated responses.

- **code-server**: An integrated development environment (IDE) accessible through the browser on port **8080**. It enables the AI Agent to execute code and scripts seamlessly.

- **Grafana**: A powerful data visualization platform that creates dashboards by querying data from QuestDB. The AI Agent updates these dashboards to provide real-time insights.

- **QuestDB**: A high-performance time-series database that serves as the central data storage for the AI Agent. It efficiently handles data querying and storage, interacting with both Grafana and the AI Agent.

- **OpenAI API**: An external API that provides advanced AI capabilities, such as natural language processing and generation. The AI Agent integrates with this API to enhance its functionality and performance.

- **Nginx**: A robust web server and reverse proxy that routes incoming user requests to the appropriate services, including the AI Agent UI, code-server, Grafana, and QuestDB.

- **Certbot**: An automated certificate management tool that simplifies the process of obtaining and renewing SSL certificates. It integrates with Nginx to enable secure communication over HTTPS.




Tasks for Intern To Do

## LangChain Integration Diagram





## LangChain-Specific Components: