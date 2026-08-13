# tests/unit/structural/test_neo4j_lookup.py

# Tests for US-5.4 AC3 (Direct read-only Cypher query).

from unittest.mock import AsyncMock, MagicMock

import pytest

from etl.graph_builder.lookup import Neo4jEntityLookupService


@pytest.mark.asyncio
async def test_find_entity_node_id_success() -> None:
    # driver.session() is a standard method that returns an async context manager
    mock_driver = MagicMock()
    mock_session_ctx = AsyncMock()
    mock_driver.session.return_value = mock_session_ctx

    mock_result = AsyncMock()
    mock_result.single.return_value = {"node_id": "element-123"}

    # Configure the actual session yielded by the context manager
    mock_session = mock_session_ctx.__aenter__.return_value
    mock_session.run.return_value = mock_result

    lookup = Neo4jEntityLookupService(mock_driver)
    node_id = await lookup.find_entity_node_id("PaymentService")

    assert node_id == "element-123"
    mock_session.run.assert_called_once()
    assert "PaymentService" in str(mock_session.run.call_args)
