# ADR-008: Documentation Connector Pattern (Push vs. Pull)

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
