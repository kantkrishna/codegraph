# ADR-011: Event Broker Selection

### Context
We need a durable message broker to route events between the ingestion APIs, the ETL workers, and the Neo4j graph builder.

### Options:
Redis Streams, RabbitMQ, Apache Kafka.

### Decision
**Apache Kafka** (via `aiokafka`). While heavier, Kafka provides ordered, replayable event logs which is critical for rebuilding historical architecture snapshots without re-querying source systems. (For local dev, we will run a single Kraft-mode Kafka container).    