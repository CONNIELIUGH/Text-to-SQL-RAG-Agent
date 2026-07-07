# RAG Text-to-SQL Agent 

A context-aware RAG text-to-SQL agent built with Python, PostgreSQL, pgvector, and Qwen3-Coder through Ollama Cloud. The agent allows users to ask natural-language business questions over Tesla operational summary data, retrieves relevant table schema context from a PostgreSQL vector database, generates SQL, validates the query for safety, executes it against PostgreSQL, and returns a final natural-language answer.

---

## Demo Video

https://www.youtube.com/watch?v=O6Rab1H_D7Y

**Video walkthrough covers:**

* Data preparation: relational PostgreSQL tables and schema documentation stored in pgvector
* Demo: example Tesla demand-related questions answered by the agent
* Agent design: context engineering, event-based workflow memory, and JSON-based LLM control flow
* Agent workflow: vector retrieval, SQL generation, SQL validation, PostgreSQL execution, and final answer generation
* Code walkthrough: main project files and backend functions

**Timestamps:**

```text
00:00 Data Preparation
02:55 Agent Design Principles
05:35 Demo
07:36 Agent Workflow Walkthrough
13:27 Code Walkthrough
```

---

## Description

I created this project because I have been exploring agentic systems, RAG, and context engineering and I wanted to combine these ideas into a practical text-to-SQL agent for business analytics.

This project is a context-aware RAG text-to-SQL agent that allows users to ask natural language business questions related to Tesla operational data from 2023, 2024, and 2025. The agent uses the Qwen3-Coder model through Ollama Cloud, PostgreSQL for relational data storage, and the `pgvector` extension as a vector database for retrieving relevant table schema context.

The database contains Tesla operational summary data, including vehicle production, vehicle deliveries, and inventory/leasing-related information. In addition to the regular relational tables, I created a vector-based schema documentation layer that stores table descriptions, column meanings, and join information as embeddings. This allows the agent to retrieve the most relevant table context before generating SQL, instead of relying only on the LLM’s internal knowledge.

The final system explores how a RAG-grounded text-to-SQL agent can help users query structured business data using natural language. The agent first understands the user’s question, retrieves relevant schema information from the PostgreSQL vector database, generates a SQL query, validates that the query is safe and read-only, executes it through backend PostgreSQL functions, and then sends the SQL result back to the LLM to produce a final natural-language answer.

I also adapted ideas from [Dexter Horthy’s 12-Factor Agents guide](https://github.com/humanlayer/12-factor-agents), which introduces principles for building more reliable LLM applications. In particular, I focused on explicit control flow and context management. The agent is instructed through system prompts to solve the user’s question step by step: first deciding whether it needs to retrieve relevant tables, then generating valid SQL, then using the SQL execution result to produce the final answer.

Since LLMs are stateless, I designed the agent to maintain an `events` variable that stores the important events from each workflow, including the original user question, LLM outputs, retrieved schema context, generated SQL, validation results, and SQL execution results. Before each LLM call, these events are rendered into a new context prompt, giving the model the full context of what has already happened in the current agent workflow.

---

## Key Features

* Natural-language question answering over structured PostgreSQL data
* RAG-based table schema retrieval using PostgreSQL + pgvector
* Text-to-SQL generation with Qwen3-Coder through Ollama Cloud
* JSON-based LLM outputs for explicit agent control flow
* Backend function calling based on model-generated intents
* SQL validation before execution (Disallow modification to database)
* Context window construction using stored workflow events
* Final natural-language answer generation based on SQL results
* Clarification handling when the user question is ambiguous

---

## Tech Stack

* **Language:** Python
* **Database:** PostgreSQL
* **Vector Database:** PostgreSQL with `pgvector`
* **LLM:** Qwen3-Coder through Ollama Cloud
* **Embedding Model:** BGE embedding model from BAAI

---

## Agent Flow Chart


<img width="460" height="758" alt="Screenshot 2026-07-06 at 12 37 18 PM" src="https://github.com/user-attachments/assets/090c98bd-a99f-4c79-803a-5645819e4e62" />
<br>
<img width="414" height="857" alt="Screenshot 2026-07-06 at 12 37 41 PM" src="https://github.com/user-attachments/assets/e6c2978b-d395-40bf-8f9c-b67c0bca46fd" />


---

## High-Level System Workflow

The project contains two main parts: the offline data/schema preparation pipeline and the online agent workflow.

### 1. Data and Schema Preparation

Tesla operational summary data is loaded into PostgreSQL as regular relational tables. Then, table schema documentation is created for each table, including table descriptions, column meanings, and join information.

Each schema document is converted into a 768-dimensional embedding vector using the BGE embedding model. These embeddings are stored in a `schema_docs` table using PostgreSQL’s `pgvector` extension.

### 2. Online Agent Workflow

When the user asks a business question, the agent does not directly ask the LLM to generate SQL. Instead, it first retrieves relevant schema context from the vector database. The retrieved context is then included in the prompt sent to the LLM.

The LLM returns structured JSON outputs with an `intent` field. Based on this intent, the backend agent decides whether to retrieve relevant tables, execute SQL, request clarification, or produce the final answer.

Before any SQL query is executed, the query is validated to make sure it is safe and read-only. After the SQL result is returned from PostgreSQL, the result is sent back to the LLM so it can generate a final natural-language answer for the user.

---

## Example Questions

Here are some example questions the agent can answer:

```text
What was the total Model 3/Y production in 2024?
```

```text
Show Tesla vehicle deliveries by quarter in 2025.
```

```text
Compare vehicle production and vehicle deliveries by quarter in 2024.
```

```text
For each quarter in 2024, was Tesla producing more vehicles than it delivered?
```

```text
Analyze the gap between Tesla vehicle production and deliveries by quarter from 2023 to 2025. Which quarters had the largest difference?
```

```text
How did operating lease vehicle counts change across quarters from 2023 to 2025?
```

The agent can also handle ambiguous or unsafe questions. For example, if the user asks a vague question, the agent can request clarification. If the user asks the agent to modify or delete data, the SQL validator blocks the query.

---

## Project Files Description

### `scripts/`

This folder contains the scripts used to prepare and load Tesla operational data into the PostgreSQL database.

#### `Create_tables.ipynb`

Creates the main relational tables in the PostgreSQL operational database:

* `vehicle_production`
* `vehicle_deliveries`
* `vehicle_inventory_leasing`

These tables store Tesla operational summary data, including production, delivery, inventory, and leasing-related information. Each table includes shared time-based columns such as `year` and `quarter`, which allows the agent to join tables across the same reporting periods.

#### `Convert_schema_embedding.py`

Creates the `schema_docs` table, which stores schema documentation for the main database tables.

Each schema document contains information such as:

* table name
* table description
* column names
* column meanings
* join information

The script converts each table’s schema documentation into a 768-dimensional embedding vector using the BGE embedding model. These embeddings are stored in PostgreSQL using the `pgvector` extension, allowing the agent to retrieve the most relevant table schemas based on the user’s question.

---

### `src/`

This folder contains the backend logic for the RAG text-to-SQL agent.

#### `config.py`

Loads environment variables from the `.env` file and provides configuration values used across the project, such as database connection settings and model/API configuration.

#### `db.py`

Contains PostgreSQL database utility functions, including:

* connecting to the PostgreSQL operational database
* executing validated read-only SQL queries
* fetching SQL execution results
* returning query outputs back to the agent workflow

#### `embeddings.py`

Contains functions for working with the BGE embedding model.

This file handles:

* loading/accessing the embedding model
* embedding schema documents
* embedding user queries with instruction text
* converting NumPy embedding vectors into string format so they can be used with `pgvector`

#### `retrieval.py`

Contains the retrieval logic for finding relevant table schemas.

This file embeds the user’s query and compares it against the stored schema embeddings in the `schema_docs` table. It then retrieves the top-k most relevant table schema documents and formats them into context that can be sent to the LLM before SQL generation.

#### `sql_validator.py`

Contains functions for validating generated SQL before execution.

The validator checks that the generated SQL query is read-only and blocks unsafe operations such as:

* `DROP`
* `DELETE`
* `UPDATE`
* `INSERT`
* `ALTER`
* `TRUNCATE`

This helps ensure that the agent can query the database without modifying or deleting data.

#### `prompts.py`

Contains the system prompts used to guide the LLM.

The prompts instruct the model to follow the agent workflow step by step and return structured JSON outputs with different `intent` values. These intents tell the backend which action to take next, such as retrieving relevant tables, executing SQL, requesting clarification, or producing the final answer.

#### `context.py`

Contains functions for managing the agent’s context window.

This file handles:

* adding new events to the workflow
* converting individual events into prompt text
* rendering all previous events into one context prompt for the LLM

Because LLMs are stateless, this context-rendering step allows the model to understand what has already happened in the current agent workflow.

#### `llm.py`

Contains functions for communicating with the Qwen3-Coder model through the Ollama Cloud API.

This file handles:

* sending prompts to the LLM
* extracting message content from the Ollama response
* parsing JSON outputs from the model response
* combining the system prompt and rendered context prompt for each LLM call

#### `agent.py`

Contains the main RAG text-to-SQL agent workflow.

This file manages the overall agent loop, including:

* storing workflow events
* calling the LLM
* reading the model’s JSON `intent`
* calling backend functions based on the intent
* retrieving relevant schema context
* validating and executing SQL
* stopping when the final answer is generated
* stopping if the maximum number of agent steps is reached

The agent uses the stored event history as a form of workflow memory, allowing each LLM call to receive an updated context window summarizing previous steps.

---

## Agent Intents

The LLM is instructed to return structured JSON outputs with an `intent` field. The backend agent uses this field to decide what action to take next.

Example intents include:

* `retrieve_relevant_tables`: retrieve the most relevant table schemas from the vector database
* `execute_sql`: validate and execute a generated SQL query
* `request_clarification`: ask the user for more information if the question is ambiguous
* `final_answer`: return the final natural-language answer to the user

This design makes the agent workflow more explicit and easier to debug because each LLM response maps to a specific backend action.

---

## SQL Safety

Since the agent generates SQL, I added a validation layer before execution. The SQL validator checks that generated queries are read-only and blocks operations that could modify or delete database records.

Blocked operations include:

```sql
DROP
DELETE
UPDATE
INSERT
ALTER
TRUNCATE
```

The agent is designed for analytical querying only, so SQL execution is limited to safe read-only operations.
