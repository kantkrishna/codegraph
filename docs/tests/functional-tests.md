# Codegraph Functional Test Suite

---

### 1. Test Prerequisites and Environment Verification

Before executing any tests, your local machine must be configured correctly.

1. **Verify Docker Desktop**: Ensure Docker Desktop is running.
* *Command*: `docker info` (Run in host terminal).
* *Expected Output*: Displays system information without connection errors.


2. **Verify `uv` Package Manager**: Ensure `uv` is installed for dependency management.


* *Command*: `uv --version` (Run in host terminal).
* *Expected Output*: `uv 0.x.x` (or similar version).


3. **Verify Environment Variables**: Create a `.env` file in the root `codegraph/` directory.

> **Exact Command to run in Host Terminal:**
> ```bash
> cat << 'EOF' > .env
> PROJECT_NAME="CodeGraph API"
> NEO4J_URI="bolt://localhost:7687"
> NEO4J_USER="neo4j"
> NEO4J_PASSWORD="codegraph_secret"
> DATABASE_URL="postgresql://postgres:codegraph_secret@localhost:5432/codegraph"
> GITHUB_APP_ID="12345"
> GITHUB_WEBHOOK_SECRET="super-secret-hmac-key"
> REDIS_URL="redis://localhost:6379"
> EOF
> 
> ```
> 
> 
> *Why*: This configures the FastAPI application and backend workers with local secrets matching the `docker-compose.yml` defaults.
> 
> 

---

### 2. Architecture & Component Inventory

Once the environment is verified, we must spin up the platform skeleton.

> **Exact Command to run in Host Terminal:**
> ```bash
> docker-compose down -v && docker-compose up -d --build
> 
> ```
> 
> 
> *Why*: This ensures no stale volumes conflict with our tests and builds the API/Worker images freshly via `uv`.
> 
> 

**Verify Component Inventory:**

* Run `docker-compose ps` in your host terminal.
* **PASS Criteria**: The following containers must display a status of "Up" (and "Healthy" where applicable):
* `codegraph-api` (FastAPI web server)
* `codegraph-worker` (Arq async background worker)
* `codegraph-neo4j` (Knowledge Graph database)
* `codegraph-postgres` (Vector/Relational database)
* `codegraph-kafka` & `codegraph-kafka-ui` (Event Broker)
* `codegraph-redis-1` (Queue backend)
* `codegraph-jaeger` (OpenTelemetry Tracing UI)





---

### 3. Test Data Setup

To validate Repository Ingestion (Epic 4), we need a deterministic test payload that simulates a GitHub Push event without needing to expose your local machine to the public internet.

> **Exact Command to run in Host Terminal:**
> ```bash
> cat << 'EOF' > simulate_webhook.py
> import hmac, hashlib, json, httpx
> SECRET = "super-secret-hmac-key"
> URL = "http://localhost:8000/api/v1/webhooks/github"
> payload = {
>     "ref": "refs/heads/main",
>     "repository": {
>         "id": 999888,
>         "clone_url": "https://github.com/octocat/Hello-World.git"
>     }
> }
> payload_bytes = json.dumps(payload).encode('utf-8')
> signature = "sha256=" + hmac.new(SECRET.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
> headers = {"X-Hub-Signature-256": signature, "X-GitHub-Event": "push", "Content-Type": "application/json"}
> response = httpx.post(URL, content=payload_bytes, headers=headers)
> print(f"Response: {response.status_code} - {response.text}")
> EOF
> 
> ```
> 
> 
> *Why*: This Python script creates a cryptographically valid HMAC SHA-256 payload perfectly mimicking GitHub's webhook behavior, targeting a lightweight public repository (`octocat/Hello-World`).
> 
> 

---

### 4. Functional Test Execution by Epic/User Story

#### Test ID: FT-1.0 (Epic 1: Platform Foundation)

* **Objective**: Prove the core API shell, database connections, and container network are running.


* **Preconditions**: `docker-compose up -d` completed successfully.
* **Exact Command**: `curl -s http://localhost:8000/health` (Host Terminal).
* **Expected Output**: `{"status":"healthy","databases":{"neo4j":"connected","postgres":"connected"}}`.


* **PASS**: HTTP 200 OK with both databases reporting "connected".
* **FAIL**: HTTP 503 or connection timeouts.
* **Evidence**: Screenshot of the JSON output and the Swagger UI accessible at `http://localhost:8000/docs`.

#### Test ID: FT-2.0 (Epic 2: Core Observability - Metrics & Logs)

* **Objective**: Validate Prometheus metrics generation and structured JSON logs with Request IDs.


* **Preconditions**: FT-1.0 passed.
* **Exact Command 1 (Metrics)**: `curl -s http://localhost:8000/metrics | grep http_requests_total` (Host Terminal).
* *Expected Output*: Prometheus counter metrics showing the `/health` endpoint invocations.




* **Exact Command 2 (Logs)**: `docker logs codegraph-api | grep http_request_completed` (Host Terminal).
* *Expected Output*: A JSON log line containing `request_id`, `method="GET"`, and `status_code=200`.




* **PASS**: Metrics contain data; logs are strict JSON with unique UUIDs per request.

#### Test ID: FT-3.0 (Epic 3: Event-Driven Infrastructure)

* **Objective**: Validate the Kafka Event Broker and Kafka UI are operational.


* **Exact Steps**:
1. Open a browser and navigate to `http://localhost:8080` (Kafka UI).


2. Click "Topics".


* **PASS**: The Kafka UI loads successfully, showing the `CodeGraph-Local` cluster in a "Healthy" or "Online" state.



#### Test ID: FT-4.0 (Epic 4: GitHub Webhook & Clone Worker)

* **Objective**: Validate secure GitHub Webhook ingestion (US-4.1) and Ephemeral Repository Cloning (US-4.2).


* **Preconditions**: `simulate_webhook.py` script created in Step 3.
* **Exact Steps & Commands**:
1. Run the webhook script: `uv run python simulate_webhook.py` (Host Terminal).
2. Read the API Response.
3. Immediately view worker logs: `docker logs codegraph-worker | tail -n 20` (Host Terminal).


* **Expected Output**:
* API Response: `202 - {"status": "accepted", "message": "Ingestion enqueued"}`.


* Worker Logs: `Cloning [https://github.com/octocat/Hello-World.git](https://github.com/octocat/Hello-World.git) into ephemeral directory: /tmp/...` followed by `Completed ingestion traversal for 999888. Ephemeral disk cleaning up.`.




* **PASS**: 202 Accepted returned. Logs prove the `arq` worker picked up the task, cloned the repo, and deleted the `/tmp` folder upon completion.

#### Test ID: FT-6.1 (Epic 6: Expanded Graph Schema V2)

* **Objective**: Validate that V1 and V2 Unique Constraints are applied to Neo4j to prevent duplicate entities.


* **Exact Command**: `uv run python scripts/apply_neo4j_constraints.py` (Host Terminal).
* **Expected Output**: Terminal prints `Applying V1 and V2 constraints...` followed by `Constraints applied successfully.`.


* **Exact Command (Verification)**: Navigate to `http://localhost:7474` in browser (Neo4j UI). Connect with `neo4j` / `codegraph_secret`. Run Cypher: `SHOW CONSTRAINTS;`
* **PASS**: The Neo4j UI lists `IS UNIQUE` constraints for labels: `Service`, `Repository`, `File`, `Class`, `Function`, `Document`, and `ADR` on the property `node_id`.



#### Test ID: FT-6.2 (Epic 6: Graph Mutation Service & Idempotency)

* **Objective**: Prove `upsert_node` and `upsert_edge` enforce ADR-026 provenance and prevent duplicates.


* **Exact Command**: `uv run python scripts/validate_neo4j_schema.py` (Host Terminal).
* **Expected Output**: The script inserts mock V1/V2 data (e.g., `ADR-01: Use Stripe` -> `PaymentService`) using `MERGE` statements.


* **PASS**: The terminal outputs `Validation PASSED: V1/V2 Schemas correctly mapped and queried.`.


* **Idempotency Proof**: Run the exact same command a second time. Go to Neo4j UI (`http://localhost:7474`), run `MATCH (n) RETURN count(n);`. The count must remain exactly the same as the first run, proving duplicates are not created.

---

### 5. End-to-End Ingestion Flow (Repository to Kafka)

**Business Flow**: GitHub Push → API Validation → Redis Queue → Async Worker → Clone → Traversal → AST/Manifest Parsing → Kafka Event Publication.

**Execution:**

1. Open Kafka UI (`http://localhost:8080`) and monitor the `events.knowledge.extracted` topic (or the exact topic verified via the Gaps section below).


2. Re-run `uv run python simulate_webhook.py` (Host Terminal).
3. Wait 10 seconds for the worker to clone and parse the repo.
4. Refresh the Kafka UI topic messages.

**What to Verify:**

* You should see strictly typed JSON payloads representing `EntityExtracted` (Classes/Functions), `DependencyDetected` (from manifests), and `RelationshipExtracted` (Imports).


* **Explicit Boundary**: The translation of these Kafka events into Neo4j nodes physically belongs to US-6.3/6.4, which are explicitly marked out of scope for this test suite. Success here is defined as the *events successfully arriving in Kafka*.

---

### 6. Observability and Telemetry Validation

We must prove that the End-to-End flow in Step 5 generated traces across service boundaries (Epic 2).

1. **OpenTelemetry Traces**:
* Navigate to `http://localhost:16686` (Jaeger UI).
* Under "Service", select `codegraph-api` and click "Find Traces".
* **What to look for**: A trace representing the `POST /api/v1/webhooks/github` request.
* Under "Service", select `codegraph-worker` (if instrumented). You should see child spans for `clone_repository_task`.


2. **Correlation Proof**:
* Expand a trace in Jaeger. Note the `Trace ID`.
* Run `docker logs codegraph-api | grep <Trace ID>`.
* **PASS**: The log payload contains the matching Trace ID, proving full correlation between structured logs and distributed tracing.




3. **Dead Letter Queue (DLQ)**:
* Stop Kafka (`docker-compose stop kafka`).
* Trigger the webhook.
* Check API logs. You should see connection retry errors or explicit DLQ routing logs depending on the exact point of failure.



---

### 7. UAT Scenario: The "Knowledge Discovery" Business Outcome

**Objective**: Demonstrate to an Engineering Manager how CodeGraph automatically discovers hidden architectural context.

**Scenario**:

1. An architect commits a new `requirements.txt` file and a `docs/adr/001-use-neo4j.md` file to a repository.
2. The GitHub App fires a webhook to CodeGraph.


3. CodeGraph securely clones the repo and filters out binary junk (US-4.1, US-4.2).


4. The `ManifestParser` reads `requirements.txt` and emits a `DependencyDetected` event for tracking security risks (US-4.4).


5. The `MarkdownWorker` recognizes the file path `docs/adr/` and uses heuristics to extract the decision status (e.g., "Accepted"), emitting an `ADRCreated` event (US-5.2).


6. **Value**: The platform has autonomously transformed flat text files into structured graph intelligence without manual data entry.
*(Note: Validate this by inspecting the Kafka UI to see the `ADRCreated` and `DependencyDetected` payloads as verified in section 5).*

---

### 8. Negative, Error, and Resilience Testing

**Test ID: NEG-1.0 (Webhook Security)**

* **Command**: `curl -X POST http://localhost:8000/api/v1/webhooks/github -H "X-Hub-Signature-256: sha256=fake" -d '{"ref":"main"}'`
* **Expected Output**: `{"detail":"Invalid GitHub Webhook Signature"}` (HTTP 401).


* **PASS**: The system actively rejects unverified payloads.

**Test ID: NEG-2.0 (Neo4j Transient Failure & Exponential Backoff)**

* **Objective**: Prove US-6.2 handles database deadlocks gracefully.
* **Preconditions**: You must run the `GraphMutationService` unit tests (which simulate `TransientError` using mocks).
* **Command**: `uv run pytest tests/integration/test_graph_mutations.py -v` (Host Terminal).
* **Expected Output**: The test simulating a transient connection loss passes because the `@with_neo4j_retries` decorator catches the failure, sleeps for `base_delay * 2^(retry-1)`, and retries successfully.


* **PASS**: The test suite passes, proving the decorator logic works.



---

### 9. Acceptance Criteria Traceability Matrix

| Epic / User Story | Verified By Test ID | Status / Notes |
| --- | --- | --- |
| **Epic 1**: Foundation & Core API | FT-1.0 | Validates FastAPI, Docker Compose, Health Check |
| **Epic 2**: Observability & Telemetry | FT-2.0, Section 6 | Validates JSON Logs, Prometheus Metrics, Jaeger |
| **Epic 3**: Event-Driven Ingestion | FT-3.0, Section 5 | Validates Kafka/KRaft, Pub/Sub mechanisms |
| **Epic 4**: Repository Ingestion | FT-4.0, NEG-1.0 | Validates Webhooks, ARQ Cloning, AST Parsing |
| **Epic 5**: Documentation Ingestion | Section 7 (UAT) | Validates ADR Heuristics, Markdown Parsing |
| **US-6.1**: Expanded Schema V2 | FT-6.1 | Validates `scripts/apply_neo4j_constraints.py` |
| **US-6.2**: Graph Mutation Service | FT-6.2, NEG-2.0 | Validates Idempotency (`MERGE`) and Backoff |

---

### 10. Gaps and Clarifications (MUST VERIFY BEFORE SIGN-OFF)

The following items are missing or ambiguous in the provided requirements and codebase. **UAT cannot be fully signed off until these are clarified.**

| Gap ID | Missing Information | Why it matters | Exact Question to Answer | How to Verify | Impact if Unresolved |
| --- | --- | --- | --- | --- | --- |
| **GAP-01** | **Kafka Topic Names** | We cannot verify E2E event flow if we check the wrong topic. | *Does the factory publish to `events.knowledge.extracted` (per codebase) or `events.ingestion.code` (per US-6.3 requirements)?* | Check `backend/services/parsers/factory.py` vs actual Kafka topics in Kafka UI. | Testers will wrongly assume the pipeline is broken because they are looking at an empty topic. |
| **GAP-02** | **Confluence Credentials** | US-5.3 requires fetching Confluence data, but no environment variables or endpoints exist to trigger it. | *How do we inject `CONFLUENCE_URL`, `EMAIL`, and `API_TOKEN`, and what scheduler triggers `ConfluenceSyncJob`?* | Review `backend/core/config.py` for Confluence variables. | **BLOCKED:** US-5.3 (Confluence Sync) cannot be functionally tested in this runbook. |
| **GAP-03** | **LLM Telemetry (US-2.4)** | The wrapper `@track_llm_telemetry` exists, but there is no LLM code in the provided scope to trigger it. | *Is the mock LLM from Epic 0 integrated into the new FastAPI structure to test token counting?* | Trigger Epic 0 impact route and check `/metrics`. | Cannot prove US-2.4 works outside of isolated unit tests. |

---

### 11. Final UAT Sign-Off Criteria

To formally accept this delivery, the QA/UAT Lead must answer **YES** to the following:

* [ ] Does `docker-compose up -d --build` successfully spin up all 7 core containers?
* [ ] Does sending a secure GitHub Webhook trigger a repository clone that automatically cleans up its temporary `/tmp` folder?
* [ ] Do `EntityExtracted` and `DependencyDetected` JSON payloads successfully arrive in Kafka?
* [ ] Are V2 Neo4j Graph Constraints (`Repository`, `Class`, `File`, `ADR`) successfully applied via the automation script?
* [ ] Does the `GraphMutationService` strictly enforce provenance (`source_system`, `timestamp`) and prevent duplicate nodes when the same payload is submitted twice?
* [ ] Are all GAP items (Section 10) documented, escalated to the engineering team, and assigned tracking tickets?

**If all criteria are met, the Foundation, Ingestion Pipeline, and Deterministic Brain (up to US-6.2) are APPROVED for progression to US-6.3.**