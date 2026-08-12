# backend/infrastructure/db.py

# This file defines the database connection utilities for the application, including
# functions to verify connections to Neo4j and PostgreSQL.

from collections.abc import Generator

import psycopg2
from neo4j import GraphDatabase
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

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


# 1. Create the SQLAlchemy Engine
# (Make sure settings.DATABASE_URL matches your actual config property for Postgres/pgvector)
# If your config uses a different name like POSTGRES_URL, replace it below.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# 2. Create the SessionLocal class factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 3. The FastAPI Database Dependency
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures
    it is closed securely after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
