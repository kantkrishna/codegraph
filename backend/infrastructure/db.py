# backend/infrastructure/db.py

# This file defines the database connection utilities for the application, including
# functions to verify connections to Neo4j and PostgreSQL.

import psycopg2
from neo4j import GraphDatabase

from backend.core.config import settings

# Neo4j Driver Singleton
neo4j_driver = GraphDatabase.driver(
    settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)


def verify_neo4j_connection() -> bool:
    try:
        neo4j_driver.verify_connectivity()
        return True
    except Exception:
        return False


def verify_postgres_connection() -> bool:
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.close()
        return True
    except Exception:
        return False
