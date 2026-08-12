# ADR-021: Repository Ingestion & Code Access Strategy

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
* **Consequences:**
* **Pros:** Highly scalable, avoids API rate limits, minimizes storage footprint, stateless workers.
* **Cons:** Requires file-system access in the worker container; unable to natively traverse historical git blame without additional API calls.


### Future Evolution
 
If we implement deep historical lineage tracking (Epic 14), we may transition to bare clones or incremental fetch strategies.