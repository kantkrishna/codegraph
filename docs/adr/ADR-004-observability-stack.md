# ADR-004: Observability Stack Selection

### Context
CodeGraph processes multi-stage pipelines: receiving a request in FastAPI, traversing a Neo4j Knowledge Graph, retrieving vector embeddings from pgvector, and assembling context for an external LLM. To maintain enterprise-grade reliability, we must monitor the latency and success rate of each individual hop.

### Problem
We need a telemetry solution (tracing and metrics) that provides immediate value during local development but can seamlessly transition to enterprise observability platforms (like Datadog, Splunk, or New Relic) in production without requiring a massive code rewrite.

### Options

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