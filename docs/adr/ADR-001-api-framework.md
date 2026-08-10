# ADR-001: API Framework & Application Architecture

### Context

CodeGraph requires a highly performant backend to handle concurrent graph traversals, vector similarity searches, and streaming LLM responses. The codebase will grow rapidly as we add connectors for GitHub, Confluence, and Jira. If we do not impose strict structural boundaries early, the AI logic, database queries, and routing will become a tangled monolith.

### Options Considered

1. **Django:** Excellent ORM, but too heavy, synchronous by default, and its ORM is not designed for Graph database (Neo4j) traversals.
2. **Flask:** Lightweight, but lacks built-in asynchronous support and strict data validation.
3. **FastAPI + Clean Architecture:** Native async, Pydantic validation, auto-generated OpenAPI docs, and easily structured into decoupled layers.

### Decision

We will use **FastAPI** with **Pydantic v2** as the core web framework.
Furthermore, we will strictly enforce **Clean Architecture** (or Hexagonal Architecture) directory structures:

* `api/`: Controllers, FastAPI routers, and HTTP request/response models.
* `domain/`: Pure business logic, core Pydantic entities (e.g., `Node`, `Edge`, `ImpactReport`).
* `services/`: Orchestration layer (e.g., `ImpactAnalysisService`).
* `infrastructure/`: Database connections (Neo4j, pgvector), LLM clients, and external API connectors.

### Consequences

* **Positive:** Complete decoupling of business logic from the HTTP layer. If we later switch from REST to gRPC or GraphQL, the domain logic remains untouched. OpenAPI documentation is generated for free.
* **Negative:** Higher initial boilerplate compared to a simple script. Developers must understand dependency injection to map interfaces in the `infrastructure` layer to the `services` layer.

---
