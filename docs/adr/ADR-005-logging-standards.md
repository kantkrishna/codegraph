# ADR-005: Logging Standards & Structure

### Context
FastAPI and Uvicorn default to unstructured, plain-text logging. In a distributed engineering intelligence platform, text logs are nearly impossible to query effectively at scale. Furthermore, our platform ingests proprietary source code and architectural data, raising significant data privacy concerns.

### Problem
We must enforce a unified logging format that is machine-readable, traceable across distributed boundaries, and secure against accidental leakage of sensitive engineering assets (like API keys in code or raw LLM prompts).

### Options

1. **Python Standard `logging` (JSON formatter):** Native, but requires heavy boilerplate to inject contextual data (like `request_id`) into every log.
2. **`Loguru`:** Highly readable, great developer experience, but slightly less flexible for strict enterprise JSON schema enforcement.
3. **`structlog`:** Industry standard for structured, contextual JSON logging in Python.

### Decision
We will implement **`structlog`** as the exclusive logging library for CodeGraph.

* **Schema:** Every log emitted will be strict JSON containing at minimum: `timestamp`, `level`, `service_name`, `request_id`, `event` (the message), and `duration` (if applicable).
* **Traceability:** We will implement a FastAPI middleware to generate a UUID `request_id` for every incoming HTTP request. `structlog` will automatically bind this ID to all logs generated during that request lifecycle.
* **Redaction:** We will configure a `structlog` processor to automatically scrub sensitive fields (e.g., `Authorization` headers, `llm_prompt_text` if not in debug mode) before the log is written.

### Consequences

* **Positive:** Logs can be instantly ingested and parsed by ELK, Datadog, or AWS CloudWatch. Searching for `request_id="abc-123"` will yield the exact lifecycle of a request, from API entry to Graph query to LLM response.
* **Negative:** Engineers must break the habit of using standard `print()` or `logging.info()`. We must enforce this via CI/CD linting (Ruff).

### Future Evolution
We will eventually expose an API endpoint to dynamically toggle the log level (e.g., from `INFO` to `DEBUG`) at runtime without restarting the application, allowing real-time debugging of production ingestion errors.
