# ADR-002: Dependency Management & Local Orchestration

**Status:** Proposed

**Date:** Current

**Epic:** Epic 1 - Platform Foundation & Core API

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
