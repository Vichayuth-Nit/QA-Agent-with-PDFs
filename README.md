# QA-Agent-with-PDFs

An multi-agent QA workflow with PDFs as RAG.

## How it work:
This workflow consist of two agent: **QA agent** and **Classifier agent**
- **Classifier agent**: An agent to classify user query from the conversation context. It will filter and ask back to user for clarification over their query. Any query that pass the classifier will going next to QA agent
- **QA agent**: An agent expertise on question answering. It connect with 2 tool by default: knowledge_base_search and DuckDuckGoSearchResults
    - knowledge_base_search: a tool connecting with PGvector service running in background. It will search for a chunk from given PDF files under directory `/papers` that user must prepared before launching service.
    - DuckDuckGoSearchResults: a wrapper for internet search. Currently using as a temporary internet search tool.

The workflow will start from `classifier_node` to classify latest user query. If `classifier_node` classify the latest query as `vague`, it will generate response requesting user to clarify and get to END point. Otherwise, the graph will pass through `agent_node` next. `agent_node` (mentioned earlier as **QA agent**) will recieved user input and make reasoning by themself whether to use `knowledge_base_search` or `DuckDuckGoSearchResults` tool to acquired an answer. This agent however, will prioritize `knowledge_base_search` first as it has been set in its system prompt.

Postgres service will always set up at start. While the pdf ingestion **will also happened at the start up as well**. Please always upload your pdf files to the directory `/papers` first before launching the docker-compsoe

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/pdfrag_agent.git
cd pdfrag_agent
```

Install dependencies (Optional):

```bash
# If using Python
pip install -r requirements.txt
```

local dependencies is not necessary as this project was build for running with Docker

**Always do these steps before going to the next step!**
- add pdf files to the local directory /papers
- change `.env_mock` file name to `.env` and add your own `OPENAI_API_KEYS`

## Running with Docker Compose

To run the agent using Docker Compose:

1. Ensure you have a `docker-compose.yml` file in the project directory.
2. Start the services:

    ```bash
    docker-compose up
    ```

3. To run in detached mode:

    ```bash
    docker-compose up -d
    ```

4. To stop the services:

    ```bash
    docker-compose down

## Possible Improvement in the future
- Improve agent prompting and tools definition to improve agent accuracy.
- Refactor: get rid of some unnecessary looping, unused import modules, and code quality for more robust speed.
- Implement `evaluator_node` to improve response accuracy
- Change llm model and embedding to more robust and up-to-date model; such as:
    - `gpt-4.1-mini` or `gemini-2.5-flash` for LLM
    - `BAAI/BGE-m3` or `gemini-embedding-001` for embedding
