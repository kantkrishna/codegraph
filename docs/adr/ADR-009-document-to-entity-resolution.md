# ADR-009: Document-to-Entity Resolution Strategy

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
