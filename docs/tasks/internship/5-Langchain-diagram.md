## Task: Build LangChain Diagram

### Instructions:
1. **File**: Use the `langchain-diagram.md` file as the destination for the diagram.
2. **Source**: Refer to the **SOTA Summary** section in `sota-summary.pdf` to build the LangChain diagram.
3. **Diagram Format**: The diagram should include key components such as:
   - **Input Processing**
   - **Language Models (LLM)** such as OpenAI or Hugging Face
   - **Chains** for sequential operations
   - **Agents** for dynamic decision-making
   - **Memory** for conversational context
   - **Tools** (databases, APIs, etc.)
   - Any **external APIs or databases** mentioned in the SOTA summary.
   
### Example Structure:

```mermaid
graph TD
    User["User<br>(Provides input)"] -->|Interacts with| LangChain

    subgraph LangChain
        InputProcessing["Input Processing<br>(Validates input)"]
        LLM["Language Model<br>(OpenAI, Hugging Face)"]
        Chains["Chains<br>(Sequence of operations)"]
        Agents["Agents<br>(Dynamic decision-making)"]
        Memory["Memory<br>(Stores state)"]
        Tools["Tools<br>(External services, retrievers)"]
    end

    LangChain -->|Processes input| InputProcessing
    InputProcessing -->|Sends request| LLM
    LLM -->|Returns response| InputProcessing

    InputProcessing -->|Feeds into| Chains
    Chains -->|Handles tasks| Agents
    Agents -->|Uses state| Memory
    Agents -->|Interacts with| Tools

    Tools -->|Queries| Database["Database<br>(e.g., QuestDB)"]
    Tools -->|Interacts with| ExternalAPI["External API<br>(e.g., OpenAI API)"]

    LangChain -->|Returns results| User



