## Architecture Overview

The following diagram illustrates the architecture of the AI Agent lab:

```mermaid
graph TD
    subgraph Docker_Services
        vscode["VSCode (Port 8080)"]
        grafana["Grafana (Port 3000)"]
        questdb["QuestDB (Port 9000, 9009, 8812, 9003)"]
        aiagentui["AI Agent UI (Port 5000)"]
        nginx["Nginx (Port 80, 443)"]
        certbot["Certbot"]
        aiagent["AI Agent\n(To be developed)"]
    end
    User -->|Interacts with| nginx
    nginx -->|Routes requests to| aiagentui
    nginx -->|Routes requests to| vscode
    nginx -->|Routes requests to| grafana
    nginx -->|Routes requests to| questdb
    aiagentui -->|Sends requests to| aiagent
    aiagent -->|Sends responses to| aiagentui
    aiagent -->|Processes data| questdb
    aiagent -->|Updates| grafana
    aiagent -->|May use| vscode
    grafana -->|Queries data from| questdb
    certbot -->|Manages SSL Certificates for| nginx
    
    nginx -.->|depends on| aiagentui
    nginx -.->|depends on| vscode
    nginx -.->|depends on| grafana
    nginx -.->|depends on| questdb
    grafana -.->|depends on| questdb
    
    aiagent -->|May connect to| OpenAI["OpenAI API"]
    
    classDef toDevelop fill:#f9f,stroke:#333,stroke-width:2px;
    class aiagent toDevelop;
```




