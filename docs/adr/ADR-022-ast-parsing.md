# ADR-022: Multi-Language AST Parsing Engine

### Context

CodeGraph must identify `Service`, `API`, `Database`, `Class`, and `Function` entities across multiple languages (Python, TypeScript, Go, Java) to populate the Knowledge Graph.

### Problem

Writing custom regex or relying on language-specific parsers (like Python's `ast` module) creates an unmaintainable, fragmented extraction pipeline.

### Options Considered

1. *Regex/Lexical Analysis:* Fast but highly inaccurate. Will fail on complex nested scopes.
2. *Language-Server Protocol (LSP):* Highly accurate but requires standing up full compiler environments for every repository.
3. *Tree-sitter:* An incremental parsing system that builds concrete syntax trees uniformly across 40+ languages without requiring compilation.

### Decision

We will adopt **Tree-sitter** as our universal AST parsing framework.
* **Consequences:**
* **Pros:** Fast, uniform syntax trees across all enterprise languages; standardizes our extraction logic; active community support.
* **Cons:** Requires compiling Tree-sitter grammars (C bindings) into our Docker images.

### Future Evolution

We will build a unified mapping layer that translates Tree-sitter outputs into our unified `Engineering Event Model` (Epic 3) so downstream systems don't need to know which language was parsed.