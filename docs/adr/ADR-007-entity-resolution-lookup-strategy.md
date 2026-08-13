# **ADR-007: Entity Resolution Lookup Strategy**

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
