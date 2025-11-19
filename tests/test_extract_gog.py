import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from source.pipeline.extract_gog import fetch_json, extract_product, extract_batch, get_all_product_ids


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.get = MagicMock()
    return session


@pytest.mark.asyncio
async def test_fetch_json_success(mock_session):
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"ok": True}

    ctx = AsyncMock()
    ctx.__aenter__.return_value = mock_response
    mock_session.get.return_value = ctx

    result = await fetch_json(mock_session, "http://example.com/data.json")
    assert result == {"ok": True}
