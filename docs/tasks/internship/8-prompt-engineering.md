## Task: Create Optimized Engineering Prompts

### Instructions:
1. **File**: Use the `prompt-engineering.md` file to document the optimized prompts you create.
2. **Objective**: The goal is to engineer prompts that return the most optimized and relevant responses from the AI model, considering clarity, conciseness, and context.

### Key Guidelines for Prompt Engineering:

- **Clarity**: Ensure the prompts are clear and free of ambiguity. The AI should understand exactly what is being asked without any confusion.
- **Context**: Provide the necessary context for the AI to generate more accurate and relevant responses. This can involve specifying the task, the expected format of the response, or any particular rules.
- **Conciseness**: Make the prompts as concise as possible while retaining the essential information. Overloading the AI with too much information might lead to less optimized responses.
- **Iterative Testing**: After crafting a prompt, test it to evaluate the responses. Modify the prompt iteratively to improve the accuracy, relevance, and efficiency of the response.

### Example Prompt Structures:

1. **Task-Oriented Prompt**:
   - Specify the task explicitly and include necessary details.
   - **Example**: "Summarize the following article in 3 concise sentences: [Insert Article Text]"

2. **Instruction-Based Prompt**:
   - Provide clear instructions on how the response should be structured or formatted.
   - **Example**: "Generate a Python function that reads a CSV file and returns a dictionary. The function should handle missing values."

3. **Question Prompt with Context**:
   - Include background information to guide the response.
   - **Example**: "Given the data on climate change trends over the past 10 years, what are the three most critical challenges facing policymakers today?"

4. **Completion Prompt**:
   - Provide the start of a response and ask the AI to complete it.
   - **Example**: "In the field of machine learning, the most common challenges are:"

5. **Multiple Prompts with Options**:
   - Provide alternative versions of a prompt to see which one generates the best response.
   - **Example**: 
     - Prompt 1: "Explain the significance of quantum computing in 2 sentences."
     - Prompt 2: "In 2 sentences, summarize the main benefits of quantum computing."

### Deliverable:
Document the following for each prompt in the **`prompt-engineering.md`** file:
- **Prompt**: The engineered prompt.
- **Objective**: The goal or task the prompt is trying to achieve.
- **Test Results**: Notes on how the AI responded to the prompt, including the relevance and optimization of the response.
- **Iterations**: If necessary, list any adjustments made to the prompt and the resulting improvements in the AI’s responses.

### Example Entry:

```markdown
### Prompt: 
"Summarize the following article in 3 concise sentences: [Insert Article Text]"

- **Objective**: To generate a brief, accurate summary of the given article.
- **Test Results**: The initial response was too detailed, exceeding the requested 3 sentences.
- **Iteration 1**: Adjusted prompt to include a limit: "Summarize the following article in exactly 3 sentences: [Insert Article Text]"
- **Outcome**: The response was concise and followed the instructions. Optimized.
