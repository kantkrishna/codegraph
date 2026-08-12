# ADR-023: Asynchronous Worker Framework

### Context

The Ingestion Pipeline (Epic 4) requires a mechanism to asynchronously clone git repositories and execute CPU-intensive AST parsing via Tree-sitter without blocking the main FastAPI web server.

### Problem

We need a reliable background task runner, but we want to avoid heavy infrastructure overhead to maintain development velocity and keep the MVP lightweight.

### Options Considered

1. *FastAPI Background Tasks:* Runs in the same event loop.
2. *ARQ / Celery (Redis-backed):* Dedicated async worker processes utilizing a lightweight message broker.
3. *Temporal / Dagster:* Enterprise-grade stateful orchestrators.

### Decision

We will use a **Redis-backed Python queue (ARQ)**.

### Consequences

* **Pros:** Keeps infrastructure dependencies strictly to Redis and Python. Excellent `asyncio` support. Prevents API blocking.
* **Cons:** Lacks the visual DAG execution monitoring and complex retry state machines provided by Temporal.
  
### Future Evolution

Once the platform proves product-market fit and the ETL pipeline grows into a multi-stage, multi-day synchronization engine, we can migrate the worker logic into Temporal without changing the core Python business logic.