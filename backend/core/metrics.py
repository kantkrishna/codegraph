# backend/core/metrics.py
#
# This file defines the Prometheus metrics for the application.

from prometheus_client import Counter, Gauge, Histogram

# --- Existing Metrics ---
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total number of HTTP requests", ["method", "path", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds", "HTTP request duration in seconds", ["method", "path"]
)

DB_ACTIVE_CONNECTIONS = Gauge("db_active_connections", "Number of active database connections")

# --- New AI & GraphRAG Telemetry Metrics (US-2.4) ---

# AC 2: LLM Tokens Counter
LLM_TOKENS_TOTAL = Counter("llm_tokens_total", "Total LLM tokens used", ["model", "token_type"])

# AC 3: LLM Generation Latency Histogram
LLM_GENERATION_DURATION_SECONDS = Histogram(
    "llm_generation_duration_seconds", "LLM generation latency in seconds", ["model"]
)
