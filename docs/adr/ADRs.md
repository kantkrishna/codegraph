# CodeGraph Architecture Decision Records (ADRs)

## Table of Contents

- [ADR-001: API Framework & Application Architecture](#adr-001-api-framework--application-architecture)
- [ADR-002: Dependency Management & Local Orchestration](#adr-002-dependency-management--local-orchestration)
- [ADR-004: Observability Stack Selection](#adr-004-observability-stack-selection)
- [ADR-005: Logging Standards & Structure](#adr-005-logging-standards--structure)
- [ADR-007: Entity Resolution Lookup Strategy](#adr-007-entity-resolution-lookup-strategy)
- [ADR-008: Documentation Connector Pattern (Push vs. Pull)](#adr-008-documentation-connector-pattern-push-vs-pull)
- [ADR-009: Document-to-Entity Resolution Strategy](#adr-009-document-to-entity-resolution-strategy)
- [ADR-011: Event Broker Selection](#adr-011-event-broker-selection)
- [ADR-012: Engineering Event Model](#adr-012-engineering-event-model)
- [ADR-021: Repository Ingestion & Code Access Strategy](#adr-021-repository-ingestion--code-access-strategy)
- [ADR-024: Knowledge Graph Ingestion Strategy](#adr-024-knowledge-graph-ingestion-strategy)
- [ADR-025: V2 Graph Ontology Expansion](#adr-025-v2-graph-ontology-expansion)
- [ADR-026: Graph Source Provenance Tracking](#adr-026-graph-source-provenance-tracking)

---

## ADR-001: API Framework & Application Architecture

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

## ADR-002: Dependency Management & Local Orchestration

### Context

Enterprise AI platforms require complex local setups. Developers will need PostgreSQL (with pgvector), Neo4j (with APOC algorithms), and Python running simultaneously. Furthermore, Python dependency hell is a notorious productivity killer in AI engineering.

### Options Considered (Python)

1. `pip` + `requirements.txt`: Too fragile, no lockfile, slow resolution.
2. `Poetry`: Standard modern choice, great lockfile, but relatively slow resolution times.
3. `uv` (by Astral): Rust-based drop-in replacement for pip/pip-tools. Blazing fast, strict lockfiles, and handles Python version management automatically.

### Decision

1. **Python Management:** We will use **`uv`** for all Python dependency management and virtual environment creation.
2. **Local Orchestration:** We will use **Docker Compose** to manage the local datastore stack. The API can be run locally on bare metal (for easier debugging) while connecting to the containerized databases, or the entire stack can be spun up via Docker.

### Consequences

* **Positive:** `uv` will cut CI/CD build times by minutes compared to Poetry. Docker Compose ensures a developer can run `docker-compose up -d` and instantly have a fully configured Neo4j and Postgres instance ready for code ingestion.
* **Negative:** Developers unfamiliar with `uv` will need a brief onboarding (which we will cover in the `README.md`).

---

## ADR-004: Observability Stack Selection

### Context

CodeGraph processes multi-stage pipelines: receiving a request in FastAPI, traversing a Neo4j Knowledge Graph, retrieving vector embeddings from pgvector, and assembling context for an external LLM. To maintain enterprise-grade reliability, we must monitor the latency and success rate of each individual hop.

### Problem

We need a telemetry solution (tracing and metrics) that provides immediate value during local development but can seamlessly transition to enterprise observability platforms (like Datadog, Splunk, or New Relic) in production without requiring a massive code rewrite.

### Options Considered

1. **Vendor-Specific SDKs (e.g., `ddtrace` for Datadog):** Powerful, but creates vendor lock-in and is difficult to run completely locally without cloud accounts.
2. **Custom Python Decorators & Logging:** Easy to implement, but lacks distributed tracing standards and visualization UIs.
3. **OpenTelemetry (OTEL):** The CNCF industry standard for vendor-agnostic instrumentation.

### Decision

We will adopt **OpenTelemetry (OTEL)** as our standard instrumentation framework.

* **Instrumentation:** We will use `opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-sqlalchemy`, and custom spans for the Neo4j driver and LLM calls.
* **Local Development Stack:** We will deploy **Jaeger** (for distributed tracing) and **Prometheus** (for metrics) alongside our Postgres and Neo4j containers in Docker Compose.
* **Production Stack:** We will configure the OTEL Exporter to route telemetry to whichever enterprise backend the organization chooses (via OTLP).

### Consequences

* **Positive:** Zero vendor lock-in. Engineers get a beautiful, visual flame-graph of request latency in local development (via Jaeger) to debug GraphRAG bottlenecks.
* **Negative:** OTEL has a slightly steeper learning curve than standard decorators, and improper span creation can introduce minor performance overhead.

### Future Evolution

As we implement the Event-Driven Pipeline (Phase 1, Epic 3), we will extend OTEL to trace asynchronous events (e.g., Kafka/RabbitMQ messages) to track a webhook from ingestion all the way to Graph update.

---

## ADR-005: Logging Standards & Structure

### Context

FastAPI and Uvicorn default to unstructured, plain-text logging. In a distributed engineering intelligence platform, text logs are nearly impossible to query effectively at scale. Furthermore, our platform ingests proprietary source code and architectural data, raising significant data privacy concerns.

### Problem

We must enforce a unified logging format that is machine-readable, traceable across distributed boundaries, and secure against accidental leakage of sensitive engineering assets (like API keys in code or raw LLM prompts).

### Options Considered

1. **Python Standard `logging` (JSON formatter):** Native, but requires heavy boilerplate to inject contextual data (like `request_id`) into every log.
2. **`Loguru`:** Highly readable, great developer experience, but slightly less flexible for strict enterprise JSON schema enforcement.
3. **`structlog`:** Industry standard for structured, contextual JSON logging in Python.

### Decision

We will implement **`structlog`** as the exclusive logging library for CodeGraph.

* **Schema:** Every log emitted will be strict JSON containing at minimum: `timestamp`, `level`, `service_name`, `request_id`, `event` (the message), and `duration` (if applicable).
* **Traceability:** We will implement a FastAPI middleware to generate a UUID `request_id` for every incoming HTTP request. `structlog` will automatically bind this ID to all logs generated during that request lifecycle.
* **Redaction:** We will configure a `structlog` processor to automatically scrub sensitive fields (e.g., `Authorization` headers, `llm_prompt_text` if not in debug mode) before the log is written.

### Consequences

* **Positive:** Logs can be instantly ingested and parsed by ELK, Datadog, or AWS CloudWatch. Searching for `request_id="abc-123"` will yield the exact lifecycle of a request, from API entry to Graph query to LLM response.
* **Negative:** Engineers must break the habit of using standard `print()` or `logging.info()`. We must enforce this via CI/CD linting (Ruff).

### Future Evolution

We will eventually expose an API endpoint to dynamically toggle the log level (e.g., from `INFO` to `DEBUG`) at runtime without restarting the application, allowing real-time debugging of production ingestion errors.

---

## ADR-007: Entity Resolution Lookup Strategy

### Context

During documentation ingestion, the platform must match textual references (e.g., "AuthService") to explicit nodes in the Knowledge Graph to create structural links.

### Problem

Should we maintain an intermediate cache (e.g., Redis) of all known graph entities for fast regex matching, or query the graph database directly as documents flow through the pipeline?

### Options Considered

1. Maintain an in-memory or Redis-based alias cache updated by `EntityExtracted` events.
2. **Query Neo4j directly during the ingestion stream.**

### Decision

We will query Neo4j directly.

### Consequences

* *Pros:* Eliminates cache invalidation bugs. Guarantees that documentation is only linked to entities that successfully exist in the persistence layer at that exact millisecond. Reduces infrastructure complexity by removing Redis from the MVP stack.
* *Cons:* Increases read I/O on Neo4j during large documentation syncs.

### Future Evolution

If Neo4j read latency becomes a bottleneck during enterprise-scale ingestion (e.g., parsing 10,000 Confluence pages simultaneously), we will introduce a read-through Redis cache.

---

## ADR-008: Documentation Connector Pattern (Push vs. Pull)

### Context

CodeGraph needs to ingest documentation from tightly coupled sources (in-repo Markdown) and external sources (Atlassian Confluence).

### Problem

In-repo documentation can be event-driven (triggered by GitHub webhooks), whereas external systems like Confluence often lack reliable enterprise webhooks or require complex firewall traversals, making real-time push difficult.

### Options Considered

1. Force all platforms to push events via webhooks.
2. Use a purely scheduled polling (pull) mechanism for all documentation.
3. **Hybrid Approach:** Event-driven for in-repo (push), and Scheduled Incremental Sync for external APIs (pull), normalizing both into a unified internal Event Data Model.

### Decision

We will use the Hybrid Approach. External connectors will implement an `IncrementalSync` interface that polls for changes since the last `Timestamp`, converting results into standard CodeGraph events (`DocumentationUpdated`).

### Consequences

* *Pros:* Maximizes real-time updates for code-adjacent docs while respecting the realities of third-party API rate limits.
* *Cons:* Requires building a scheduling mechanism (e.g., Celery/APScheduler) for the pull-based connectors.

### Future Evolution

As the Plugin Framework (Epic 16) matures, this Incremental Sync interface will become the standard SDK for future integrations like Jira, Notion, or SharePoint.

---

## ADR-009: Document-to-Entity Resolution Strategy

### Context

Extracting text is insufficient; CodeGraph must link documentation to specific microservices, repositories, or APIs to calculate metrics like "Documentation Freshness".

### Problem

How do we programmatically determine which code component a specific Confluence page or Markdown file is describing?

### Options Considered

1. Rely entirely on the LLM to read the document and guess the associated service (expensive, slow).
2. **Heuristic-First, AI-Second:** Extract frontmatter tags (e.g., `service: PaymentService`), parse folder structures (e.g., `docs/architecture/`), and use regex matching against known entities. Fall back to LLM semantic matching only if heuristics fail.

### Decision

Implement the Heuristic-First strategy. The ingestion worker will emit a `DocumentationLinked` event when explicit references are found.

### Consequences

* *Pros:* Fast, cheap, and highly accurate for mature teams that use YAML frontmatter or standard ADR templates.
* *Cons:* Teams with poorly structured documentation will have orphaned docs in the graph until the AI semantic matcher is implemented in Phase 3.

### Future Evolution

We will introduce a "Knowledge Governance" dashboard (Epic 15) to flag unlinked documentation so human architects can manually associate them.

---

## ADR-011: Event Broker Selection

### Context

We need a durable message broker to route events between the ingestion APIs, the ETL workers, and the Neo4j graph builder.

### Options Considered

Redis Streams, RabbitMQ, Apache Kafka.

### Decision

**Apache Kafka** (via `aiokafka`). While heavier, Kafka provides ordered, replayable event logs which is critical for rebuilding historical architecture snapshots without re-querying source systems. (For local dev, we will run a single Kraft-mode Kafka container).

---

## ADR-012: Engineering Event Model

### Context

How do we standardize the schema of events across the platform?

### Decision

We will adopt the **CloudEvents** specification (v1.0) wrapped in strict Pydantic models to ensure cross-language compatibility if we write future plugins in Go or TypeScript.

---

## ADR-021: Repository Ingestion & Code Access Strategy

### Context

To analyze code, CodeGraph needs access to enterprise repositories. We must decide how to fetch and store source code during the ingestion pipeline without overwhelming memory or violating security boundaries.

### Problem

Large enterprise monorepos can be massive (gigabytes). Relying on GitHub API tree fetching is slow and subject to harsh rate limits. Full `git clone` operations include heavy historical `.git` data that we do not need for structural point-in-time parsing.

### Options

1. *GitHub REST/GraphQL API:* Fetch files one by one. (Too slow, high risk of rate-limiting).
2. *Full Git Clone:* Use `GitPython` to clone the repo to a persistent volume. (Heavy storage overhead, requires stateful workers).
3. *Ephemeral Shallow Clone:* Execute a shallow, single-branch clone (`git clone --depth 1`) to ephemeral disk storage inside a worker node, process it, and wipe the disk.


### Decision

We will use **Ephemeral Shallow Clones** triggered by a background worker queue (e.g., Celery or arq).

### Consequences

* **Pros:** Highly scalable, avoids API rate limits, minimizes storage footprint, stateless workers.
* **Cons:** Requires file-system access in the worker container; unable to natively traverse historical git blame without additional API calls.

### Future Evolution
 
If we implement deep historical lineage tracking (Epic 14), we may transition to bare clones or incremental fetch strategies.

---

## ADR-024: Knowledge Graph Ingestion Strategy

### Context
Epics 4 and 5 generate thousands of discrete, asynchronous Kafka events (`EntityExtracted`, `DependencyDetected`, `DocumentationUpdated`). We must insert these into Neo4j without causing race conditions or deadlocks.

### Problem
Concurrent asynchronous workers attempting to create interconnected nodes (e.g., Worker A creates a `Function` node; Worker B creates a `Class` node containing that function) will crash if the graph operations are not strictly idempotent.

### Options Considered
* Batch processing via nightly ETL pipelines.
* Reactive, asynchronous Cypher `MERGE` operations via Kafka consumers.
* Using an intermediate caching layer (Redis) to lock nodes during updates.

### Decision
We will use reactive, asynchronous Cypher `MERGE` operations handled by a centralized Graph Mutation Service. We will rely on Neo4j's native transaction management and unique constraints to handle concurrency safely.

### Consequences
`MERGE` is computationally heavier than `CREATE`. We must ensure strict `IS UNIQUE` constraints on `node_id` exist before any workers are started to prevent full database scans during the `MERGE` operation.

### Future Evolution
If throughput exceeds Neo4j's write capacity, we will introduce a micro-batching mechanism within the Kafka consumer loop to group `MERGE` statements.

---

## ADR-025: V2 Graph Ontology Expansion

### Context
Epic 0 established a V1 schema focused purely on high-level architecture (`Service`, `API`, `Database`). We now have low-level code and documentation data flowing from Epics 4 and 5.

### Problem
We need a standardized way to represent code structures and documentation inside the graph so they can be linked to the V1 architecture nodes.

### Decision
We will expand the ontology to include new node labels: `Repository`, `File`, `Class`, `Function`, `Document`, and `ADR`. We will introduce structural edges: `CONTAINS` (Repo -> File, File -> Class), `IMPLEMENTS` (Class -> Function), and `DOCUMENTS` (Document -> Service).

### Consequences
The graph will grow rapidly in density. We must strictly enforce pagination and depth limits on all future Cypher traversal queries to prevent memory explosion.

### Future Evolution
We will eventually introduce temporal versioning nodes (e.g., `Commit`, `Branch`) in Phase 5 to track schema drift over time.

---

## ADR-026: Graph Source Provenance Tracking

### Context
In an enterprise, an architectural relationship (e.g., "Service A calls Database B") might be asserted by a parsed Python file, a Markdown document, or an explicitly written ADR.

### Problem
If conflicting relationships are extracted, or if an edge needs to be invalidated because a file is deleted, the graph must know exactly *where* that edge came from.

### Decision
Every single edge (relationship) in the Knowledge Graph must contain standard provenance properties: `source_system` (e.g., GitHub, Confluence), `source_uri` (e.g., the file path or URL), `commit_sha` (if applicable), and `timestamp`.

### Consequences
Storage requirements for relationships will increase. Cypher queries must be written to UPSERT these properties if the edge already exists.

### Future Evolution
This provenance data will directly power the "Knowledge Confidence Score" calculated in Epic 11.