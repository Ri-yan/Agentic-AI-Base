# Genric Agents

> **Purpose:** This repository implements **Graphy**, an analytics-focused conversational agent that analyzes schema information and user queries to generate validated chart/dashlet payloads and query templates. It supports multiple agent frameworks (LangChain, LangGraph, CrewAI) and is organized to separate API, agent orchestration, tools, and use-cases.

---

## Table of contents

1. Project overview
2. Quickstart (run locally)
3. Environment & configuration
4. API endpoints (examples)
5. High-level architecture (ASCII diagram)
6. Component-by-component breakdown
7. JobHuntings use-case: flow and templates
8. Models, validators & tools
9. How the agent is constructed (agent factory / selectors)
10. Logging, guardrails & memory
11. Tests, debugging & troubleshooting
12. Deployment & production notes
13. Extensions, improvements & TODOs

---

## 1. Project overview

This project provides a modular agent platform focused on analytics (chart/dashlet generation). The major goals:

* Accept a user prompt + schema details and return chart-ready JSON payloads.
* Validate model outputs with Pydantic models (SchemaModel, GraphDataModel, QueryConfigModel).
* Support multiple underlying agent runtimes (LangChain, LangGraph, CrewAI).
* Provide pluggable tools (generate chart/dashlet/query handler) and memory backends.

Key strengths:

* Clear separation of concerns (API ↔ usecases ↔ agent wrapper ↔ tools ↔ LLM)
* Pydantic-based validation for deterministic outputs
* Flexible agent factory to plug different frameworks

## 2. Quickstart (run locally)

**Prerequisites**

* Python 3.11+
* An OpenAI API key (or other model provider depending on your AGENT\_FRAMEWORK)

**Install**

```bash
# create conda env (recommended)
conda create -n genric-agents python=3.11 -y
conda activate genric-agents

# install dependencies
pip install -r requirements.txt

```

**Set environment variables** (example):

```bash
export OPENAI_API_KEY="sk-..."
export AGENT_FRAMEWORK=langgraph   # or langchain / crewai
export OPENAI_MODEL=gpt-4o-mini
```

**Run the API**

```bash
# option A: run directly
python main.py
# option B: uvicorn
uvicorn main:app --reload --port 8025
```

The app will be available at `http://localhost:8025`.

## 3. Environment & configuration

The project loads environment variables from `resources/config.env` via `resources/constant.load_environs()`.

Important variables:

* `AGENT_FRAMEWORK` — one of `langchain`, `langgraph`, `crewai`. Determines which agent implementation is used.
* `OPENAI_API_KEY` — required for OpenAI-based LLM usage.
* `OPENAI_MODEL` — model name (e.g. `gpt-4o-mini`).
* `MULTI_NODE_AGENT` — (project-specific) toggle for multi-node behavior.

**Agent config files** are in `config/agents/` (e.g. `analytics_agent_config.json`). These files define agent identity, guardrails, topics and capabilities used by the agent factory.

## 4. API endpoints (examples)

`POST /api/agent/chat` — main entrypoint for session-based agent runs.

* Request model: `AgentQuery` (fields: `sessionId`, `prompt`, `payload`)

Example `curl` request:

```bash
curl -X POST http://localhost:8025/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session-123",
    "prompt": "Show me monthly leads by source",
    "payload": {
      "schema_details": {"table_name":"LeadsBaseView","db_type":"mssql","fields":[]},
      "query": "monthly leads split by source"
    }
  }'
```

`POST /api/genai/run` — directly invokes the `AdvanceAnalyticsUseCase` with arbitrary dict payload for quick testing.

Response shape (standardized by `utilities.response.build_response`):

```json
{
  "status": true,
  "message": "",
  "response": {
     "Data": {...},
     "AIMessage": "...",
     "ToolMessage": "...",
     "Reasoning": "..."
  }
}
```

## 5. High-level architecture (ASCII diagram)

```
+----------+    HTTP   +----------------+    create/get    +--------------------+
|  Client  | ----->   | FastAPI (main) | --------------->  | Agent Manager /     |
+----------+          +----------------+                   |  BaseAgent          |
                                                           +--------------------+
                                                                    |
                                                                    | selects
                                                                    v
                                               +-------------------------------------------+
                                               | Agent Selector (LangChain / LangGraph /   |
                                               |  CrewAI) -> returns a framework-specific   |
                                               |  agent wrapper (LangChainAgentWrapper etc.)|
                                               +-------------------------------------------+
                                                                    |
                                             +----------------------+-----------------+
                                             |                                        |
                                         LLM / Guardrails                      Tools & Memory
                                       (create_llm via llm_factory)          (tool_factory, memory_factory)
                                             |                                        |
                                             v                                        v
                                 +---------------------------+           +-----------------------------+
                                 | Use Case / Prompt Chains  | <-------> | Tool implementations (,
                                 | ()|           |  ) |
                                 +---------------------------+           +-----------------------------+
                                                                    |
                                                                    v
                                                           +--------------------+
                                                           | Validators (pydantic)|
                                                           +--------------------+
                                                                    |
                                                                    v
                                                           +--------------------+
                                                           |  API returns JSON   |
                                                           +--------------------+
```

## 6. Component-by-component breakdown

**`main.py`**

* FastAPI entry with `app.include_router(routes, prefix='/api')`. Starts uvicorn.

**`api/routes.py`**

* Defines REST endpoints `/agent/chat` and `/genai/run`.
* Uses `services.agent_executor.run_agent_query` for session-based calls.

**`services/agent_executor.py`**

* Thin shim that calls `agents_builder.agent_manager.get_agent` (factory) and `agent.run(...)`.

**`agents_builder/`**

* `agent_config_loader.py` — loads JSON agent configs from `config/agents/`.
* `agent_manager.py` — creates and caches agents per session (in-memory `agent_store`). Wraps tools to match differing tool signatures across frameworks.
* `base_agent.py` — constructs the agent implementation using `agents_builder.selector.select_agent`.
* `tool_factory.py` — adapts local Python functions into framework-specific tools (LangChain `Tool`, CrewAI `BaseTool`, etc.).
* `memory_factory.py` — provides memory backends for each supported framework (LangChain conversation memory or CrewAI memory wrappers).
* `selector/` — contains per-framework constructors: `langchain_selector.py`, `langgraph_selector.py`, `crewai_selector.py`. Each wraps the LLM, memory and tools into a framework-specific agent and exposes a unified `run` interface.

**`usecases/analytics_gpt/charts_genrator_usecase/`**

* Implements the `AdvanceAnalyticsQueryGenerator` use case which:

  * analyzes query intent (QueryConfig)
  * generates a SchemaModel describing fields/filters/group/order
  * generates GraphData (chart config) suitable for front-end widgets
  * validates all intermediate outputs using Pydantic models
* Contains `templates/` for LLM prompts, `models/` for Pydantic models, `tools/` and `validators/`.

**`tools/`**

* Global tools that can be mounted onto agents: `generate_chart_tool`, `generate_dashlet_tool`, `query_handler_tool`. These call into the AdvanceAnalytics generator or other helpers.

**`resources/`**

* `config.env` default env variables
* Logging helpers `resources/Logging/studio_logger.py`

**`utilities/response.py`**

* Standardized response builder used across wrappers.

## 7. Advance Analytics use-case: flow and templates

Core flow (inside `AdvanceAnalyticsQueryGenerator.generate`):

1. **Query analysis** — run query analysis template to classify the user request and produce `QueryConfig` (isValidQuery, multiResponse, widgetType, fieldsMentioned, etc.).
2. **Schema model generation** — If valid and a chart-type request, generate a `SchemaModel` describing Fields, Filters, GroupBy, OrderBy, BatchSize and other schema related metadata.
3. **Graph (chart) generation** — Using `SchemaModel` and graph-type preferences, generate `GraphDataModel` payloads for frontend visualizations.
4. **Validation** — Each raw LLM output is parsed and validated via Pydantic models in `validators.validators._validate_model`. This removes common LLM output wrappers (`json` etc.) and ensures strict typing.
5. **Filtering & Tooling** — `fields_filter_tool` is used to map natural-language mentions to actual schema fields.

The use-case uses multiple templated prompts (in `templates/`) to keep each step focused and reproducible.

## 8. Models, validators & tools

**Pydantic models** (key ones):

* `QueryConfigModel` — intent classification and metadata
* `SchemaModelOutput` — Fields/Filters/Group/Order structure
* `GraphDataModel` — Chart payload (graphs, categoryField, dataProvider, axes)

**Validators** ensure the LLM outputs strictly conform to the expected schema; they also strip markdown/code fences commonly emitted by LLMs.

**Tools**

* `fields_filter_tool` — simple keyword partial-matching filter that returns candidate field definitions.
* `generate_chart_tool` / `generate_dashlet_tool` — thin wrappers which call the AdvanceAnalytics generator and return `utilities.response.build_response` style objects.

## 9. How the agent is constructed (agent factory / selectors)

Flow when a request comes in:

1. `services.agent_executor.run_agent_query` calls `agents_builder.get_agent` (see `agent_manager.py`).
2. The agent manager: loads config (per-agent or default), selects tools from `tools.ALL_TOOLS`, wraps them to framework-compatible signatures, then constructs a `BaseAgent(config, tools)` instance.
3. `BaseAgent` delegates to `agents_builder.selector.select_agent` which returns a framework-specific wrapper (LangChainAgentWrapper, LangGraphAgentWrapper or CrewAIAgentWrapper).
4. Wrapper initializes an LLM (via `llm.llm_factory.create_llm`), memory (via `memory_factory`) and constructs agent internals (chains, tools, guardrails, system prompt).
5. When `agent.run(prompt, payload)` is called, the wrapper executes the agent flow and returns a standardized response using `utilities.response.build_response`.

## 10. Logging, guardrails & memory

* **Guardrails**: `guardrails/sys_guards.py` contains a system-level instruction applied to agents to reduce hallucinations and enforce step-by-step reasoning.
* **Logging**: `resources/Logging/studio_logger.py` returns a simple Python `logging` instance per use-case.
* **Memory**: `agents_builder/memory_factory.py` adapts either LangChain conversation memories or CrewAI memory classes. Currently the project ships with adapters to produce conversation buffers or long-term memory where available.

## 11. Tests, debugging & troubleshooting

**Common issues & fixes**

* `OPENAI_API_KEY` not found: ensure `resources/config.env` is filled or set environment variables before starting.
* `AGENT_FRAMEWORK` mismatch: set `AGENT_FRAMEWORK` to one of `langchain`, `langgraph`, `crewai`. If a framework is missing in your environment (e.g. `crewai` not installed), either install it or pick another framework.
* Import errors (langchain/langgraph version mismatches): ensure versions in `requirements.txt` are installed. LangChain/LangGraph have breaking changes across major versions — pin the working versions from `requirements.txt`.
* LLM output formatting errors: validators may raise when the LLM returns non-JSON results. Inspect `templates/` to tune instructions and add stricter output schema.

**Debugging tips**

* Enable debug logs via python logging configuration.
* Run `uvicorn main:app --reload` and call endpoints with simple payloads first.
* Re-run a failing step manually: the AdvanceAnalytics class exposes `_generate_chain_run` type methods — wrap them to print raw LLM output to debug.

## 12. Deployment & production notes

* **Secrets**: never store `OPENAI_API_KEY` in repo. Use secret stores (AWS Secrets Manager, HashiCorp Vault) in production.
* **Scaling**: the agent store is an in-memory dict. For multiple instances / horizontal scaling, move session storage to Redis or a persistent store and share agent state or only store immutable configs in DB.
* **Rate limiting & concurrency**: LLM calls are rate-limited and can be slow. Add request queuing, timeouts and circuit-breakers around LLM calls.
* **Persistent memory**: For long-term memory or multi-session context, integrate a vector DB (Weaviate, Pinecone, Chroma) and adapt `memory_factory` to use it.
* **Observability**: add structured traces around LLM calls and tool calls (e.g. OpenTelemetry), and log LLM tokens usage for cost control.

## 13. Extensions, improvements & TODOs

**Short-term**

* Add unit tests for `validators._validate_model` and `fields_filter_tool`.
* Harden prompt templates (provide examples and negative examples to reduce hallucination).
* Add request/response tracing (e.g. request ID headers).

**Medium-term**

* Add a vector store backed memory implementation and persistence across restarts.
* Add a dashboard showing recent sessions, requests and token usage.
* Add more sophisticated field matching (fuzzy match, name synonyms, embedding-based similarity).

**Long-term / Research**

* Multi-agent coordination: compose multiple agents (ETL-agent, Query-agent, Viz-agent) into pipelines.
* Offline deterministic generation: explore using function-calling APIs or structured output specs to guarantee correct JSON output.

---

## Appendix: file map (important files)

```
main.py                          # FastAPI entry
api/routes.py                    # API endpoints
agents_builder/                  # Agent factory, tool adapter, memory adapter
  - agent_manager.py
  - base_agent.py
  - tool_factory.py
  - memory_factory.py
  - selector/ (langchain, langgraph, crewai)
usecases/analytics_gpt/          # Advance analytics use-case, templates, validators
tools/                           # application-level tools mounted into agents
resources/                       # config.env + logging
utilities/response.py            # standard response format
config/agents/analytics_agent_config.json  # agent metadata and guardrails
```

