

# Architecture Overview

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
- **AI Agent**: The main AI service that handles requests from the AI Agent UI and interacts with **QuestDB**, **Grafana**, and **code-server**. It also communicates with the **OpenAI API** for natural language processing tasks.
- **AI Agent UI**: The user interface (Flask-based), handling user requests and returning AI Agent responses.
- **code-server**: Added as a service running on port **8080**, allowing the AI Agent to execute code.
- **Grafana**: Visualizes data by querying QuestDB, with updates handled by the AI Agent.
- **QuestDB**: The core database for querying and storing data, interacting with both Grafana and the AI Agent. 
- **OpenAI API**: External API for AI capabilities, like generating responses based on user input, integrated with the AI Agent.
- **Nginx**: Acts as a reverse proxy, routing user requests to **AI Agent UI**, **code-server**, **Grafana**, and **QuestDB**.
- **Certbot**: Manages SSL certificates for secure communication, integrated with Nginx.




