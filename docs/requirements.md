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
  * [Epic 3: Event-Driven Ingestion Architecture](#epic-3-event-driven-ingestion-architecture)
* [Phase 2: Structural Knowledge Extraction (The Deterministic Brain)](#phase-2-structural-knowledge-extraction-the-deterministic-brain)
  * [Epic 4: Repository Ingestion (ASTs & Dependencies)](#epic-4-repository-ingestion-asts--dependencies)
  * [Epic 5: Documentation Ingestion](#epic-5-documentation-ingestion)
  * [Epic 6: Knowledge Graph Builder](#epic-6-knowledge-graph-builder)
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
## Epic 3: Event-Driven Ingestion Architecture
  * *Rationale:* Promoted from Epic 15. The prompt demands incremental updates (no full rebuilds). We must lay down the Event Bus (e.g., handling `CommitDetected`, `ServiceAdded` events) before writing any ingestion logic.

---

# Phase 2: Structural Knowledge Extraction (The Deterministic Brain)

## Epic 4: Repository Ingestion (ASTs & Dependencies)
  * *Rationale:* Connects to GitHub, clones code, and parses Abstract Syntax Trees.
## Epic 5: Documentation Ingestion
  * *Rationale:* Ingests Markdown, Confluence, and ADRs.
## Epic 6: Knowledge Graph Builder
  * *Rationale:* Moved up. Takes the parsed data from Epics 4/5 and translates it into deterministic Neo4j nodes/edges *before* we do any semantic vectorization.

---

# Phase 3: Semantic Processing (The Probabilistic Brain)

## Epic 7: Graph-Aware Chunking Framework
  * *Rationale:* Now that the graph exists, we chunk the code and docs. Because we have the graph, chunks can be tagged with the `node_id` of the service/function they belong to.
## Epic 8: Embedding Pipeline & Vector Store
  * *Rationale:* Generates standard dense embeddings (OpenAI/SentenceTransformers) and stores them in pgvector, linked to the chunks.

---

# Phase 4: Intelligence & Delivery (The User Value)

## Epic 9: Hybrid Retrieval (Graph Traversal + Vector Search)
  * *Rationale:* Fuses BM25, semantic search, and Cypher queries to assemble context.
## Epic 10: RAG Evaluation & Query Engine
  * *Rationale:* (Split from old Testing Epic). Before exposing this to users, we implement semantic routing and quantitative RAG evaluation (e.g., Ragas/TruLens) to ensure the LLM isn't hallucinating dependencies.
## Epic 11: Engineering Intelligence
  * *Rationale:* Builds the specific business logic (Dependency Risk Score, Blast Radius, Architecture Drift) utilizing the Query Engine.
## Epic 12: Frontend Experience (Web UI)
  * *Rationale:* Consumes the APIs to build the React/Next.js dashboard, Graph visualization, and Chat UI.

---

# Phase 5: Enterprise Scale & Governance (Production Readiness)

## Epic 13: Production Readiness & Deployment
  * *Rationale:* Hardening, Kubernetes manifests, security scanning, and final MVP launch.
## Epic 14: Version-Aware Knowledge Management
  * *Rationale:* Advanced feature to track temporal shifts (Branch A vs. Branch B).
## Epic 15: Knowledge Governance & Security
  * *Rationale:* Handling RBAC, data permissions, and source provenance.
## Epic 16: Plugin Framework & Connectors
  * *Rationale:* SDK to allow enterprise teams to write custom Jira/Notion plugins.
## Epic 17: Platform SDK & Analytics
  * *Rationale:* Releasing the Python/TS SDKs for developers, alongside platform usage analytics dashboards.
