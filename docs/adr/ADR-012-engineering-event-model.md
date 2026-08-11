# ADR-012: Engineering Event Model

### Context
How do we standardize the schema of events across the platform?

### Decision
We will adopt the **CloudEvents** specification (v1.0) wrapped in strict Pydantic models to ensure cross-language compatibility if we write future plugins in Go or TypeScript.