# Epics and User Stories of Codegraph: Enterprise AI-Augmented Engineering Platform

## Table of Contents

* [Epic 0: Impact Analysis Prototype](#epic-0-impact-analysis-prototype)
  * [US-0.1: Design Knowledge Graph Schema for Architecture Topology](#us-01-design-knowledge-graph-schema-for-architecture-topology)
  * [US-0.2: Implement Cypher Traversal for Blast Radius Calculation](#us-02-implement-cypher-traversal-for-blast-radius-calculation)
  * [US-0.3: LLM Context Assembly & Risk Scoring](#us-03-llm-context-assembly--risk-scoring)
  * [US-0.4: Expose Impact Analysis via FastAPI](#us-04-expose-impact-analysis-via-fastapi)
* [Phase 1: Foundation & Event Architecture (The Skeleton)](#phase-1-foundation--event-architecture-the-skeleton)
  * [Epic 1: Platform Foundation & Core API](#epic-1-platform-foundation--core-api)
    * [US-1.1: Initialize Monorepo and Development Environment](#us-11-initialize-monorepo-and-development-environment)
    * [US-1.2: Containerize Local Development Stack](#us-12-containerize-local-development-stack)
    * [US-1.3: Build Core FastAPI Application Shell](#us-13-build-core-fastapi-application-shell)
    * [US-1.4: Implement CI Pipeline Quality Gates](#us-14-implement-ci-pipeline-quality-gates)
  * [Epic 2: Core Observability & Telemetry](#epic-2-core-observability--telemetry)
    * [US-2.1: Standardize Structured JSON Logging](#us-21-standardize-structured-json-logging)
    * [US-2.2: Implement Distributed Tracing (OpenTelemetry)](#us-22-implement-distributed-tracing-opentelemetry)
    * [US-2.3: Expose Application Metrics Endpoint](#us-23-expose-application-metrics-endpoint)
    * [US-2.4: LLM & GraphRAG Telemetry Foundation](#us-24-llm--graphrag-telemetry-foundation)
  * [Epic 3: Event-Driven Ingestion Architecture](#epic-3-event-driven-ingestion-architecture)
    * [US-3.1: Deploy Local Event Broker Infrastructure](#us-31-deploy-local-event-broker-infrastructure)
    * [US-3.2: Define the Engineering Event Data Model](#us-32-define-the-engineering-event-data-model)
    * [US-3.3: Implement Publisher & Consumer Routing](#us-33-implement-publisher--consumer-routing)
    * [US-3.4: Dead Letter Queue (DLQ) & Resilience Mechanisms](#us-34-dead-letter-queue-DLQ--resilience-mechanisms)
* [Phase 2: Structural Knowledge Extraction (The Deterministic Brain)](#phase-2-structural-knowledge-extraction-the-deterministic-brain)
  * [Epic 4: Repository Ingestion (ASTs & Dependencies)](#epic-4-repository-ingestion-asts--dependencies)
    * [US-4.1: Secure Source Code Provider Integration (GitHub App)](#us-41-secure-source-code-provider-integration-github-app)
    * [US-4.2: Asynchronous Repository Clone Worker](#us-42-asynchronous-repository-clone-worker)
    * [US-4.3: AST Entity Extraction via Tree-sitter](#us-43-ast-entity-extraction-via-tree-sitter)
    * [US-4.4: Application Dependency & Relationship Extraction](#us-44-application-dependency--relationship-extraction)
  * [Epic 5: Documentation Ingestion](#epic-5-documentation-ingestion)
    * [US-5.1: In-Repository Markdown Parsing](#us-51-in-repository-markdown-parsing)
    * [US-5.2: Architecture Decision Record (ADR) Extraction](#us-52-architecture-decision-record-adr-extraction)
    * [US-5.3: Confluence Incremental Sync Connector](#us-53-confluence-incremental-sync-connector)
    * [US-5.4: Document-to-Entity Linking Worker](#us-54-document-to-entity-linking-worker)
  * [Epic 6: Knowledge Graph Builder](#epic-6-knowledge-graph-builder)
    * [US-6.1: Define and Apply Expanded Graph Schema (V2)](#us-61-define-and-apply-expanded-graph-schema-v2)
    * [US-6.2: Implement Graph Mutation Service](#us-62-implement-graph-mutation-service)
    * [US-6.3: Code Entity Event Consumer](#us-63-code-entity-event-consumer)
    * [US-6.4: Documentation Event Consumer](#us-64-documentation-event-consumer)
* [Phase 3: Semantic Processing (The Probabilistic Brain)](#phase-3-semantic-processing-the-probabilistic-brain)
  * [Epic 7: Graph-Aware Chunking Framework](#epic-7-graph-aware-chunking-framework)
  * [Epic 8: Embedding Pipeline & Vector Store](#epic-8-embedding-pipeline--vector-store)
* [Phase 4: Intelligence & Delivery (The User Value)](#phase-4-intelligence--delivery-the-user-value)
  * [Epic 9: Hybrid Retrieval (Graph Traversal + Vector Search)](#epic-9-hybrid-retrieval-graph-traversal--vector-search)
  * [Epic 10: RAG Evaluation & Query Engine](#epic-10-rag-evaluation--query-engine)
  * [Epic 11: Engineering Intelligence](#epic-11-engineering-intelligence)
  * [Epic 12: Frontend Experience (Web UI)](#epic-12-frontend-experience-web-ui)
* [Phase 5: Enterprise Scale & Governance (Production Readiness)](#phase-5-enterprise-scale--governance-production-readiness)
  * [Epic 13: Production Readiness & Deployment](#epic-13-production-readiness--deployment)
  * [Epic 14: Version-Aware Knowledge Management](#epic-14-version-aware-knowledge-management)
  * [Epic 15: Knowledge Governance & Security](#epic-15-knowledge-governance--security)
  * [Epic 16: Plugin Framework & Connectors](#epic-16-plugin-framework--connectors)
  * [Epic 17: Platform SDK & Analytics](#epic-17-platform-sdk--analytics)

---

# Epic 0: Impact Analysis Prototype

## Business Value

Provide engineering teams with immediate visibility into the blast radius of proposed architectural or code changes, reducing integration bugs, deployment failures, and unknown downstream effects.

## Scope of Vertical Slice

Instead of boiling the ocean and indexing an entire enterprise, our MVP will simulate a constrained environment (e.g., a microservices architecture with a frontend, a few backend services, a database, and a message queue). The AI must traverse this specific graph to answer: *"If I modify X, what breaks?"*

## User Stories Breakdown

### US-0.1: Design Knowledge Graph Schema for Architecture Topology

* **Description:** Define the Neo4j node and edge structures required to represent services, APIs, databases, and message queues.
* **Acceptance Criteria:**

  * Schema successfully maps `(Service)-[:CALLS]->(API)` and `(Service)-[:PUBLISHES]->(Event)`.
  * Schema supports querying downstream and upstream dependencies.
* **Story Points:** 3

### US-0.2: Implement Cypher Traversal for Blast Radius Calculation

* **Description:** Create the core backend logic that takes a target node (e.g., `PaymentService`) and traverses outbound/inbound edges up to a depth of 3 to map the impact zone.
* **Acceptance Criteria:**

  * API endpoint accepts a node ID and returns a JSON subgraph of impacted components.
  * Traversal respects a configured maximum depth to prevent graph explosion.
* **Story Points:** 5

### US-0.3: LLM Context Assembly & Risk Scoring

* **Description:** Feed the extracted Cypher subgraph into the LLM context window to generate a human-readable risk report and assign a "Dependency Risk Score".
* **Acceptance Criteria:**

  * LLM correctly identifies which downstream services might fail.
  * Output includes a Risk Score (Low, Medium, High, Critical) based on the number of dependent critical nodes.
* **Story Points:** 5

### US-0.4: Expose Impact Analysis via FastAPI

* **Description:** Build the REST API layer so the frontend (or future CLI) can query the Impact Analysis engine.
* **Acceptance Criteria:**

  * Endpoint `POST /api/v1/intelligence/impact` is available and documented via OpenAPI.
* **Story Points:** 2

---

# Phase 1: Foundation & Event Architecture (The Skeleton)

## Epic 1: Platform Foundation & Core API
  * *Rationale:* Sets up the monorepo, CI/CD, Docker configurations, base FastAPI routing, and database connections. We need a running system on day one.

## User Stories Breakdown

### US-1.1: Initialize Monorepo and Development Environment

- **Description:** Establish the project's physical structure, dependency management, and code quality tools to ensure all engineers follow the same standards.

- **Acceptance Criteria:**

- Project structure follows the defined Clean Architecture directories (`backend/api`, `backend/core`, `backend/domain`, etc.).

- Dependency management is configured using `Poetry` or `uv`.

- Code quality tools (Ruff, Mypy, Pre-commit hooks) are installed and configured.

- A basic `README.md` and `CONTRIBUTING.md` are present.

- **Business Value:** Prevents technical debt and ensures code consistency across the engineering team from the start.

- **Priority:** Highest (P0)

- **Dependencies:** None

- **Technical Notes:** Enforce strict type checking in Mypy. Use Ruff for replacing Black/Flake8/isort to speed up pre-commit times.

- **Story Points:** 2

- **Definition of Done:** Pre-commit hooks pass locally, and the structure is merged to the `main` branch.

### US-1.2: Containerize Local Development Stack

- **Description:** Create a unified local execution environment using Docker Compose so developers can spin up the API and all backing datastores with a single command.

- **Acceptance Criteria:**

- `docker-compose.yml` includes the FastAPI backend service.

- `docker-compose.yml` includes a Neo4j container (with APOC plugin).

- `docker-compose.yml` includes a PostgreSQL container (with `pgvector` extension).

- Local state/volumes are mapped appropriately to persist data between container restarts.

- **Business Value:** Eliminates the "it works on my machine" problem and dramatically speeds up developer onboarding.

- **Priority:** Highest (P0)

- **Dependencies:** US-1.1

- **Technical Notes:** Use multi-stage Dockerfiles for the Python backend to optimize the final image size.

- **Story Points:** 3

- **Definition of Done:** `docker-compose up` successfully starts all services, and datastores accept local connections.

### US-1.3: Build Core FastAPI Application Shell

- **Description:** Implement the foundational FastAPI application with standardized routing, Pydantic configuration management, and global exception handling.

- **Acceptance Criteria:**

- FastAPI app initializes successfully.

- Dependency Injection container (or standard FastAPI `Depends`) is set up for database sessions.

- Global exception handlers are implemented to return standardized JSON error responses.

- A `GET /health` endpoint returns 200 OK and checks connections to Neo4j and Postgres.

- **Business Value:** Provides a secure, scalable, and self-documenting API layer (OpenAPI/Swagger) for all future AI and Graph features.

- **Priority:** High (P1)

- **Dependencies:** US-1.1, US-1.2

- **Technical Notes:** Use Pydantic `BaseSettings` for environment variable validation. Implement CORS middleware early.

- **Story Points:** 5

- **Definition of Done:** Unit tests pass for the health endpoint, and the Swagger UI is accessible locally at `http://localhost:8000/docs`.

### US-1.4: Implement CI Pipeline Quality Gates

- **Description:** Set up GitHub Actions to enforce quality gates on every Pull Request.

- **Acceptance Criteria:**

- CI pipeline triggers on PRs to `main`.

- Pipeline runs Ruff (linting), Mypy (type checking), and Pytest (unit tests).

- Pipeline builds the Docker image to ensure there are no build regressions.

- Branch protection rules are configured to require passing CI before merge.

- **Business Value:** Protects the main branch from regressions, broken builds, and degraded code quality.

- **Priority:** High (P1)

- **Dependencies:** US-1.1, US-1.3

- **Technical Notes:** Use GitHub Actions caching for Python dependencies to speed up CI runs.

- **Story Points:** 2

- **Definition of Done:** A test PR successfully triggers and passes the CI pipeline.

---

## Epic 2: Core Observability & Telemetry
  * *Rationale:* Pulled from the end of the backlog. We must instrument structured logging, tracing (OpenTelemetry), and basic DB metrics *before* we start pushing gigabytes of code through pipelines.

## User Stories Breakdown

### US-2.1: Standardize Structured JSON Logging

- **Description:** Replace standard Python logging with a structured JSON logger (e.g., `structlog` or `loguru`). Every log entry must include contextual metadata (`request_id`, `environment`, `service_name`) to allow enterprise log aggregators (Datadog, Splunk, ELK) to parse and index them efficiently.

- **Acceptance Criteria:**

- All FastAPI routes output logs in purely JSON format.

- A unique `request_id` is injected into every incoming HTTP request via middleware.

- The `request_id` is automatically propagated to all log entries generated during that request lifecycle.

- Sensitive data (e.g., API keys, Authorization headers) is masked/redacted in the logging middleware.

- **Business Value:** Reduces Mean Time to Resolution (MTTR) by allowing engineers to query logs systematically rather than grepping text files.

- **Priority:** High (P0)

- **Dependencies:** Epic 1 (FastAPI Foundation)

- **Technical Notes:** Recommend `structlog`. Use standard Python logging for third-party libraries but capture and format them through the structured logging pipeline.

- **Story Points:** 3

- **Definition of Done:** Code merged, unit tests pass, JSON logs verified in standard output, documentation updated.

**Task Breakdown (US-2.1):**

- **Task 1: Configure Structlog setup**

- *Complexity:* Low

- *Dependencies:* None

- *Expected Files:* `backend/core/logger.py`, `backend/core/config.py`

- *Testing:* Unit tests verifying JSON output format.

- **Task 2: Implement FastAPI Request ID Middleware**

- *Complexity:* Medium

- *Dependencies:* Task 1

- *Expected Files:* `backend/api/middleware/logging_middleware.py`, `backend/main.py`

- *Testing:* Integration tests ensuring `request_id` matches across request lifecycle.

### US-2.2: Implement Distributed Tracing (OpenTelemetry)

- **Description:** Instrument the application with OpenTelemetry (OTEL) to track request flows across boundaries (FastAPI -> PostgreSQL -> Neo4j -> External LLM API).

- **Acceptance Criteria:**

- OTEL SDK is initialized at application startup.

- FastAPI requests generate spans automatically.

- Database queries (SQLAlchemy/pgvector and Neo4j Python Driver) are instrumented and generate child spans.

- Traces are exported to a local tracing backend (e.g., Jaeger or Zipkin) running in Docker Compose.

- **Business Value:** Provides complete visibility into latency bottlenecks, especially critical for multi-stage GraphRAG pipelines where a slow Cypher query could degrade the user experience.

- **Priority:** High (P0)

- **Dependencies:** US-2.1

- **Technical Notes:** Use `opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-sqlalchemy`.

- **Story Points:** 5

- **Definition of Done:** Spans successfully visible in local Jaeger UI for standard API requests.

**Task Breakdown (US-2.2):**

- **Task 1: Setup OpenTelemetry SDK & FastAPI Instrumentation**

- *Complexity:* Medium

- *Dependencies:* None

- *Expected Files:* `backend/core/telemetry.py`, `backend/main.py`

- *Testing:* Unit test mocking the span exporter.

- **Task 2: Instrument Neo4j and PostgreSQL connections**

- *Complexity:* Medium

- *Dependencies:* Task 1

- *Expected Files:* `backend/core/database.py`, `backend/core/graph_db.py`

- *Testing:* Integration tests validating DB queries create child spans.

- **Task 3: Add Jaeger to Docker Compose local stack**

- *Complexity:* Low

- *Dependencies:* None

- *Expected Files:* `docker/docker-compose.yaml`

- *Testing:* Verify Jaeger UI is accessible at `localhost:16686`.

### US-2.3: Expose Application Metrics Endpoint

- **Description:** Expose a `/metrics` endpoint to serve Prometheus-compatible metrics. Track standard application health metrics (request count, latency distributions) and establish a framework for custom Engineering Intelligence metrics later.

- **Acceptance Criteria:**

- Endpoint `GET /metrics` exists and returns Prometheus text format.

- Tracks HTTP request duration (Histogram).

- Tracks total HTTP requests (Counter) by status code and path.

- Tracks current active database connections (Gauge).

- **Business Value:** Enables proactive alerting (e.g., alerting the on-call engineer if the 95th percentile latency of graph traversals exceeds 2 seconds).

- **Priority:** Medium (P1)

- **Dependencies:** None

- **Technical Notes:** Use `prometheus-client` and standard FastAPI middleware for metrics.

- **Story Points:** 3

- **Definition of Done:** Endpoint returns properly formatted data, passing load test checks without degrading API performance.

**Task Breakdown (US-2.3):**

- **Task 1: Build Prometheus Metrics Middleware**

- *Complexity:* Medium

- *Dependencies:* None

- *Expected Files:* `backend/api/middleware/metrics_middleware.py`, `backend/core/metrics.py`

- *Testing:* E2E test making multiple requests and asserting counter increments.

- **Task 2: Expose /metrics route safely**

- *Complexity:* Low

- *Dependencies:* Task 1

- *Expected Files:* `backend/api/routers/system.py`

- *Testing:* API test asserting 200 OK and text/plain response.

### US-2.4: LLM & GraphRAG Telemetry Foundation

- **Description:** Create specialized telemetry wrappers for LLM calls to track prompt tokens, completion tokens, costs, and model latency. This is essential for controlling cloud costs and measuring AI generation performance.

- **Acceptance Criteria:**

- Custom OTEL spans created specifically for LLM calls.

- Metrics counters established for `llm_tokens_total` (labeled by model and prompt/completion).

- Latency histograms created for `llm_generation_duration_seconds`.

- **Business Value:** Provides strict governance and FinOps capabilities to monitor the financial cost of running the Engineering Intelligence platform.

- **Priority:** Medium (P1)

- **Dependencies:** US-2.2, US-2.3

- **Technical Notes:** Create a reusable decorator or base class for all external AI interactions that automatically handles the token tracking.

- **Story Points:** 3

- **Definition of Done:** Dummy LLM call implemented in tests triggers token counters and span generation.

**Task Breakdown (US-2.4):**

- **Task 1: Design AI Telemetry Decorator/Wrapper**
- *Complexity:* High
- *Dependencies:* US-2.2
- *Expected Files:* `backend/core/ai_telemetry.py`
- *Testing:* Unit tests asserting correct token counting and metrics logging using mock OpenAI responses.

---

## Epic 3: Event-Driven Ingestion Architecture
  * *Rationale:* Promoted from Epic 15. The prompt demands incremental updates (no full rebuilds). We must lay down the Event Bus (e.g., handling `CommitDetected`, `ServiceAdded` events) before writing any ingestion logic.

## User Stories Breakdown

#### US-3.1: Deploy Local Event Broker Infrastructure

* **Description:** Containerize and configure the local development event broker (Kafka in KRaft mode) and establish the foundational backend connection managers.
* **Acceptance Criteria:**
* Kafka runs successfully in `docker-compose.yml` without Zookeeper.
* FastAPI backend connects to the broker on startup and gracefully disconnects on shutdown.
* Broker exposes an admin UI (e.g., Kafka UI) on a local port for developer observability.

* **Business Value:** Provides the reliable, high-throughput transport layer necessary for processing thousands of repository files concurrently.
* **Priority:** P0 (Highest)
* **Dependencies:** Epic 1 & 2 Completed.
* **Technical Notes:** Use `aiokafka` for async, non-blocking I/O. Integrate broker connection states into the FastAPI health check endpoint.
* **Story Points:** 3
* **Definition of Done:** Infrastructure is running, health checks pass, CI/CD pipeline starts the broker successfully during integration tests.

**Task Breakdown:**

* *Task 1:* Add Kafka (KRaft mode) and Kafka-UI to `docker-compose.yml`. (Complexity: Low)
* *Task 2:* Create `backend/core/events/broker.py` with async connection management. (Complexity: Medium)
* *Task 3:* Update FastAPI lifespan events to handle broker connect/disconnect. (Complexity: Low)
* *Task 4:* Write Pytest fixture for the event broker. (Complexity: Medium)

#### US-3.2: Define the Engineering Event Data Model

* **Description:** Create strict, polymorphic Pydantic schemas for the platform's core domain events to ensure schema validation at the producer level.
* **Acceptance Criteria:**
* Base `CodeGraphEvent` class implements the CloudEvents specification (id, source, specversion, type, datacontenttype, time).
* Specific payload schemas exist for `RepositoryIndexed`, `CommitDetected`, `ServiceAdded`, and `DocumentationUpdated`.
* Validation fails immediately if an invalid payload is published.

* **Business Value:** Prevents "poison pill" messages from crashing consumer microservices by enforcing strict data contracts.
* **Priority:** P0
* **Dependencies:** US-3.1
* **Technical Notes:** Utilize Pydantic's `Discriminator` and `Union` types for polymorphic event parsing.
* **Story Points:** 2
* **Definition of Done:** Mypy passes, schemas are fully unit-tested with valid and invalid JSON payloads.

**Task Breakdown:**

* *Task 1:* Create `backend/domain/events/base.py` for CloudEvents wrapper. (Complexity: Low)
* *Task 2:* Define payload schemas in `backend/domain/events/ingestion.py`. (Complexity: Medium)
* *Task 3:* Write unit tests verifying Pydantic discriminator routing. (Complexity: Low)

#### US-3.3: Implement Publisher & Consumer Routing

* **Description:** Build the Python framework that allows services to publish events to topics, and allows background workers to subscribe to topics and process events asynchronously.
* **Acceptance Criteria:**
* `EventPublisher.publish(event: CodeGraphEvent)` abstraction is implemented.
* A consumer loop can listen to a specific topic (e.g., `events.ingestion`) and route the event to a registered handler function based on the event `type`.
* Consumers automatically inject trace IDs into OpenTelemetry context (from Epic 2).

* **Business Value:** Decouples platform modules. The GitHub webhook handler can just "fire and forget", while the graph builder works at its own pace.
* **Priority:** P0
* **Dependencies:** US-3.1, US-3.2
* **Technical Notes:** Implement consumer loops as asyncio background tasks managed by the FastAPI lifespan or a separate CLI worker entrypoint.
* **Story Points:** 5
* **Definition of Done:** Integration test successfully publishes a test event and a dummy consumer receives and logs it.

**Task Breakdown:**

* *Task 1:* Implement `EventPublisher` wrapper using `AIOKafkaProducer`. (Complexity: Medium)
* *Task 2:* Implement `EventConsumer` loop using `AIOKafkaConsumer`. (Complexity: High)
* *Task 3:* Implement the router/registry mapping event types to handler functions. (Complexity: Medium)
* *Task 4:* Integrate OpenTelemetry context propagation in headers. (Complexity: High)

#### US-3.4: Dead Letter Queue (DLQ) & Resilience Mechanisms

* **Description:** Ensure that if an event fails to process (e.g., Neo4j is temporarily down, or LLM parsing fails), the message is not lost but routed to a Dead Letter Queue for later retry or manual intervention.
* **Acceptance Criteria:**
* If a consumer raises an unhandled exception, the event is acknowledged but republished to a `dlq.<topic_name>` topic.
* Logs (from Epic 2) capture the original exception, event ID, and DLQ routing action.

* **Business Value:** Ensures zero data loss. Missing a commit event could mean missing a critical architectural dependency change.
* **Priority:** P1
* **Dependencies:** US-3.3
* **Technical Notes:** Implement this as a decorator or middleware on the consumer handler functions.
* **Story Points:** 3
* **Definition of Done:** End-to-end test verifying a forced failure results in message appearance in the DLQ topic.

**Task Breakdown:**

* *Task 1:* Create consumer middleware/decorator for exception catching. (Complexity: Medium)
* *Task 2:* Implement DLQ publishing logic. (Complexity: Low)
* *Task 3:* Create integration tests for forced consumer failures. (Complexity: Medium)

---

# Phase 2: Structural Knowledge Extraction (The Deterministic Brain)

## Epic 4: Repository Ingestion (ASTs & Dependencies)
  * *Rationale:* Connects to GitHub, clones code, and parses Abstract Syntax Trees.

## User Story Breakdown

### US-4.1: Secure Source Code Provider Integration (GitHub App)

* **Description:** As a Platform Administrator, I need to connect CodeGraph to my GitHub Organization via a GitHub App so that the platform can securely authenticate and listen to repository events.
* **Acceptance Criteria:**
* System supports GitHub App installation (OAuth/JWT authentication).
* Webhook endpoint securely receives payload and validates HMAC signatures.
* Webhook pushes a `RepositoryIngestionRequested` event to the Event Bus.

* **Business Value:** Establishes secure, standard enterprise access without relying on individual developer Personal Access Tokens (PATs).
* **Dependencies:** Epic 3 (Event Bus must be available).
* **Technical Notes:** Use PyGithub with JWT for App authentication. Store private keys securely via Pydantic Settings/Vault.
* **Story Points:** 5
* **Definition of Done:** Code merged, unit tests pass (mocking GitHub API), webhook payload validation verified, observability traces active.

### US-4.2: Asynchronous Repository Clone Worker

* **Description:** As the Ingestion Pipeline, I need to react to `RepositoryIngestionRequested` events by asynchronously downloading the code so that the main API remains non-blocking.
* **Acceptance Criteria:**
* Background worker consumes the event and performs a shallow clone (`--depth 1`).
* Clones to an ephemeral, isolated `/tmp` directory inside the worker container.
* Traverses the directory, filters out ignored files (`.gitignore`, binaries).
* Emits `FileDiscovered` events to the Event Bus for each valid source file.
* Cleans up the ephemeral directory upon completion or failure.

* **Business Value:** Ensures the platform can ingest massive enterprise repositories without crashing the main API layer.
* **Priority:** High
* **Story Points:** 8
* **Definition of Done:** Worker deployed, integration test validates successful clone and cleanup of a sample repo, disk usage metrics tracked in Datadog/Prometheus.

### US-4.3: AST Entity Extraction via Tree-sitter

* **Description:** As the Ingestion Pipeline, I need to parse source files into Abstract Syntax Trees so that I can extract structural engineering entities (Classes, Functions, Methods).
* **Acceptance Criteria:**
* Worker consumes `FileDiscovered` events.
* Detects language (Python, JS/TS) and applies the correct Tree-sitter grammar.
* Extracts structural nodes (e.g., class names, function signatures, docstrings).
* Normalizes and publishes these as `EntityExtracted` events.

* **Business Value:** Moves the platform beyond naive text chunking into true semantic code understanding.
* **Dependencies:** US-4.2.
* **Technical Notes:** Focus purely on Python and TypeScript for the MVP. Create a generalized interface for adding Go/Java later.
* **Story Points:** 8
* **Definition of Done:** Unit tests validate correct extraction of classes/functions for Python and TS files.

### US-4.4: Application Dependency & Relationship Extraction

* **Description:** As the Ingestion Pipeline, I need to extract import statements and package manifests so that CodeGraph can map internal and external dependencies.
* **Acceptance Criteria:**
* Parses standard package files (`requirements.txt`, `pyproject.toml`, `package.json`).
* Traverses AST to extract file-to-file import relationships.
* Publishes `DependencyDetected` and `RelationshipExtracted` events to the Event Bus.

* **Business Value:** Provides the raw edge data needed to calculate blast radius and dependency risk scores.
* **Story Points:** 5
* **Definition of Done:** Pipeline successfully identifies internal cross-file imports and external package dependencies in the sample data repository.

---

## Epic 5: Documentation Ingestion
  * *Rationale:* Ingests Markdown, Confluence, and ADRs.

## User Story Breakdown

### US-5.1: In-Repository Markdown Parsing

* **Title:** Parse In-Repository Markdown and Emits Events
* **Description:** As the Ingestion Pipeline, I need to process discovered `.md` files so that their structural content (frontmatter, headers, body) can be normalized and broadcasted to the platform.
* **Acceptance Criteria:**
* Worker consumes `FileDiscovered` events (from US-4.2) and filters for Markdown extensions.
* Parses YAML frontmatter into a structured metadata dictionary.
* Strips invalid characters and normalizes file paths.
* Publishes a `DocumentationUpdated` event to the Event Bus containing the normalized text, metadata, and repository provenance.

* **Business Value:** Unlocks architectural knowledge stored directly next to the source code, reducing knowledge silos.
* **Priority:** High (P0)
* **Dependencies:** US-3.3 (Event Routing), US-4.2 (Repository Clone Worker).
* **Technical Notes:** Use `python-frontmatter` or `markdown-it-py`. Ensure the event payload matches the polymorphic `CodeGraphEvent` schema.
* **Story Points:** 5
* **Definition of Done:** Integration tests confirm a pushed `.md` file results in a validated `DocumentationUpdated` event in the Kafka topic.
* **Task Breakdown:**
1. **Task 1: Build Markdown Parser Utility** Build a Markdown parser utility in etl/connectors/markdown/parser.py and unit test it with valid and malformed files.
2. **Task 2: Implement FileDiscovered Event Handler** Implement a `FileDiscovered` event handler in `etl/connectors/markdown/worker.py` and test for `DocumentationUpdated` emission.

### US-5.2: Architecture Decision Record (ADR) Extraction

* **Title:** Extract Structured Metadata from ADRs
* **Description:** As the Ingestion Pipeline, I need to recognize ADR files and specifically extract their context, status, and decisions so that architectural evolution can be tracked as distinct graph entities.
* **Acceptance Criteria:**
* Pipeline identifies ADRs using path heuristics (e.g., `docs/adr/`, `architecture/decisions/`).
* Regex/heuristic parser specifically extracts the "Status" (e.g., Proposed, Accepted, Deprecated) and "Decision" blocks.
* Emits the specialized `ADRCreated` engineering event.

* **Business Value:** Enables the platform to answer "Why was this database chosen?" and tracks the historical timeline of architectural drift.
* **Priority:** High (P1)
* **Dependencies:** US-5.1
* **Technical Notes:** ADRs often follow the MADR (Markdown Any Decision Record) format. Build the parser to handle standard heading variations.
* **Story Points:** 3
* **Definition of Done:** Pipeline successfully identifies an ADR in the sample repo, parses the status, and emits the exact `ADRCreated` event.
* **Task Breakdown:**
1. **Task 1: Build ADR-Specific Parsing Logic** Build and unit-test an ADR-specific parser in `etl/connectors/markdown/adr_parser.py` to extract status from MADR templates.
2. **Task 2: Integrate into Markdown Worker** Integrate the parser into etl/connectors/markdown/worker.py and run E2E tests for event routing.

### US-5.3: Confluence Incremental Sync Connector

* **Title:** Implement Confluence Cloud API Connector
* **Description:** As a Platform Administrator, I need CodeGraph to periodically sync documents from a specified Confluence Cloud space so that external enterprise tribal knowledge is ingested. *Note: Confluence Data Center (on-prem) is explicitly out of scope for the MVP.*
* **Acceptance Criteria:**
* System accepts Confluence Cloud credentials (URL, Email, API Token).
* Worker queries the Confluence Cloud REST API `/wiki/api/v2/pages` filtered by `lastModified`.
* Converts Atlassian Document Format (ADF) or HTML to normalized Markdown.
* Emits `DocumentationUpdated` events.

* **Business Value:** Captures business requirements, meeting notes, and runbooks that do not live in Git repositories, without over-complicating MVP infrastructure with on-premise networking.
* **Priority:** Medium (P2)
* **Dependencies:** US-3.1 (Event Bus)
* **Technical Notes:** Use `atlassian-python-api`. Implement a basic scheduler (e.g., `asyncio` loop or lightweight APScheduler) to trigger the sync every X minutes.
* **Story Points:** 8
* **Definition of Done:** Worker successfully paginates through a mock Confluence space, converts HTML to Markdown, and emits events.
* **Task Breakdown:**
1. **Task 1: Confluence Cloud API Client Wrapper:** Build HTTP client tailored strictly to Atlassian Cloud authentication headers.
2. **Task 2: ADF/HTML to Markdown Converter:** Parse Atlassian-specific markup to standard markdown.
3. **Task 3: Polling Scheduler and State Management:** Implement basic schedule loop to pull incremental changes.

### US-5.4: Document-to-Entity Linking Worker

* **Title:** Heuristic Document Entity Linking (Direct Graph Query)
* **Description:** As the Knowledge Graph Builder, I need documentation events to contain metadata linking them to recognized code entities (Services, Repos) so I can create edges in the graph.
* **Acceptance Criteria:**
* A downstream worker listens to `DocumentationUpdated` and `ADRCreated` events.
* Worker extracts potential entity names/aliases from the document text and frontmatter.
* Worker directly executes a read-only Cypher query against Neo4j to verify if the entity exists.
* If verified, publishes a `DocumentationLinked` event containing the `doc_id` and the matched Neo4j `node_id`.

* **Business Value:** Creates the crucial connective tissue between text and code with 100% data consistency, enabling accurate GraphRAG queries.
* **Priority:** High (P1)
* **Dependencies:** US-5.1, US-5.2, Epic 1 (Neo4j Connection)
* **Story Points:** 5
* **Definition of Done:** The worker successfully matches a Confluence page mentioning "AuthService" to the internal AuthService entity ID and publishes the linkage event.
* **Task Breakdown:**
1. **Task 1: Implement Neo4j Entity Lookup Service:** Create a read-only Cypher utility in `etl/graph_builder/lookup.py` optimized for batch matching alias names to node IDs.
2. **Task 2: Linkage Processor & Event Emitter:** Create the worker that listens to doc events, calls the lookup service, and emits `DocumentationLinked` if a match is found in the database.

---

## Epic 6: Knowledge Graph Builder
  * *Rationale:* Moved up. Takes the parsed data from Epics 4/5 and translates it into deterministic Neo4j nodes/edges *before* we do any semantic vectorization.

---


### US-6.1: Define and Apply Expanded Graph Schema (V2)

**Description:** Apply Neo4j unique constraints for the expanded code and documentation ontology to prevent duplicate nodes during asynchronous event ingestion.
**Acceptance Criteria:**

* Unique constraints exist for `Repository`, `File`, `Class`, `Function`, `Document`, and `ADR` labels using the `node_id` property.
* Epic 0 constraints (`Service`, `API`, `Database`) remain intact and functional.
* An automated validation script runs in the CI pipeline to verify schema enforcement on an empty database.
**Business Value:** Ensures structural data integrity at the database level, preventing the AI from hallucinating duplicate architectures.
**Dependencies:** Epic 1 (Neo4j Infrastructure).
**Story Points:** 2
**Definition of Done:** Python constraint application script is updated, executed successfully against the local Docker Neo4j instance, and merged to `main`.

| Task | Complexity | Expected Files |
| --- | --- | --- |
| Task 1: Update Neo4j constraint automation script to include V2 labels | Low | `scripts/apply-neo4j-constraints.py` |
| Task 2: Update mock data validation script to test new node uniqueness | Low | `scripts/validate-neo4j-schema.py` |

---

### US-6.2: Implement Graph Mutation Service

**Description:** Create a core backend service that wraps the Neo4j Python driver. This service will expose standardized, idempotent methods for Upserting nodes and edges, preventing individual consumers from writing raw Cypher.
**Acceptance Criteria:**

* Service exposes an `upsert_node(label, properties)` method utilizing Cypher `MERGE`.
* Service exposes an `upsert_edge(source_id, target_id, rel_type, properties)` method.
* Edge upserts strictly enforce the inclusion of the provenance fields defined in ADR-026.
* Deadlocks or transient Neo4j connection errors trigger automatic retries using exponential backoff.
**Business Value:** Centralizes database write logic, making the system significantly easier to maintain, audit, and secure.
**Dependencies:** US-6.1.
**Story Points:** 5
**Definition of Done:** Unit tests achieve 90%+ coverage on the mutation service, demonstrating successful retries and idempotent writes.

| Task | Complexity | Expected Files |
| --- | --- | --- |
| Task 1: Build the GraphMutationService class with basic `MERGE` templates | Medium | `backend/graph/mutation_service.py` |
| Task 2: Implement exponential backoff and retry logic for transaction failures | Medium | `backend/core/decorators.py` |
| Task 3: Write integration tests verifying idempotent node and edge creation | High | `tests/integration/test_graph_mutations.py` |

---

### US-6.3: Code Entity Event Consumer

**Description:** Build the Kafka consumer worker that listens to AST-derived events (`EntityExtracted`, `DependencyDetected`) and uses the Graph Mutation Service to build the structural code graph.
**Acceptance Criteria:**

* Consumer subscribes to the `events.ingestion.code` topic.
* `EntityExtracted` events are translated into `File`, `Class`, and `Function` nodes with `CONTAINS` edges.
* `DependencyDetected` events are translated into `DEPENDS_ON` or `IMPORTS` edges between files or repositories.
* OpenTelemetry spans (from Epic 2) successfully wrap the consumer execution and database writes.
**Business Value:** Automatically translates raw repository code into a queryable, connected map of engineering dependencies.
**Dependencies:** US-6.2, Epic 3 (Event Broker), Epic 4 (AST Events).
**Story Points:** 8
**Definition of Done:** End-to-end integration test proves that publishing a mock `EntityExtracted` event results in the correct nodes appearing in Neo4j.

| Task | Complexity | Expected Files |
| --- | --- | --- |
| Task 1: Register the Kafka consumer loop for code events | Medium | `etl/graph_builder/code_consumer.py` |
| Task 2: Implement the routing logic mapping event schemas to mutation methods | High | `etl/graph_builder/routers.py` |
| Task 3: Inject OpenTelemetry trace contexts from the event payload into the DB spans | Medium | `etl/graph_builder/telemetry.py` |

---

### US-6.4: Documentation Event Consumer

**Description:** Build the Kafka consumer worker that listens to documentation events (`DocumentationUpdated`, `ADRCreated`, `DocumentationLinked`) and connects enterprise knowledge to the code graph.
**Acceptance Criteria:**

* Consumer subscribes to the `events.ingestion.docs` topic.
* `DocumentationUpdated` events generate `Document` nodes.
* `ADRCreated` events generate `ADR` nodes containing status and decision properties.
* `DocumentationLinked` events (from US-5.4) generate `DOCUMENTS` edges connecting the text node to the corresponding structural node (e.g., `Service`).
**Business Value:** Bridges the gap between what the code does and what the engineers wrote about it, preventing knowledge silos.
**Dependencies:** US-6.2, Epic 5 (Documentation Events).
**Story Points:** 5
**Definition of Done:** Querying the local Neo4j database successfully returns an `ADR` node connected via a `DOCUMENTS` edge to a `Service` node.

| Task | Complexity | Expected Files |
| --- | --- | --- |
| Task 1: Register the Kafka consumer loop for documentation events | Medium | `etl/graph_builder/doc_consumer.py` |
| Task 2: Implement edge creation logic specifically for heuristic entity linkages | Medium | `etl/graph_builder/linkage_service.py` |

# Phase 3: Semantic Processing (The Probabilistic Brain)

## Epic 7: Graph-Aware Chunking Framework
  * *Rationale:* Now that the graph exists, we chunk the code and docs. Because we have the graph, chunks can be tagged with the `node_id` of the service/function they belong to.

---

## Epic 8: Embedding Pipeline & Vector Store
  * *Rationale:* Generates standard dense embeddings (OpenAI/SentenceTransformers) and stores them in pgvector, linked to the chunks.

---

# Phase 4: Intelligence & Delivery (The User Value)

## Epic 9: Hybrid Retrieval (Graph Traversal + Vector Search)
  * *Rationale:* Fuses BM25, semantic search, and Cypher queries to assemble context.

---

## Epic 10: RAG Evaluation & Query Engine
  * *Rationale:* (Split from old Testing Epic). Before exposing this to users, we implement semantic routing and quantitative RAG evaluation (e.g., Ragas/TruLens) to ensure the LLM isn't hallucinating dependencies.

---

## Epic 11: Engineering Intelligence
  * *Rationale:* Builds the specific business logic (Dependency Risk Score, Blast Radius, Architecture Drift) utilizing the Query Engine.

---

## Epic 12: Frontend Experience (Web UI)
  * *Rationale:* Consumes the APIs to build the React/Next.js dashboard, Graph visualization, and Chat UI.

---

# Phase 5: Enterprise Scale & Governance (Production Readiness)

## Epic 13: Production Readiness & Deployment
  * *Rationale:* Hardening, Kubernetes manifests, security scanning, and final MVP launch.

---

## Epic 14: Version-Aware Knowledge Management
  * *Rationale:* Advanced feature to track temporal shifts (Branch A vs. Branch B).

---

## Epic 15: Knowledge Governance & Security
  * *Rationale:* Handling RBAC, data permissions, and source provenance.

---

## Epic 16: Plugin Framework & Connectors
  * *Rationale:* SDK to allow enterprise teams to write custom Jira/Notion plugins.

---

## Epic 17: Platform SDK & Analytics
  * *Rationale:* Releasing the Python/TS SDKs for developers, alongside platform usage analytics dashboards.
