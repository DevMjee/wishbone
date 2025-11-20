"""Tests for the extract_gog script"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from extract_gog import fetch_json, extract_product, extract_batch, get_all_product_ids


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


@pytest.mark.asyncio
async def test_fetch_json_404(mock_session):
    mock_response = AsyncMock()
    mock_response.status = 404

    ctx = AsyncMock()
    ctx.__aenter__.return_value = mock_response
    mock_session.get.return_value = ctx

    result = await fetch_json(mock_session, "http://example.com/failure")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_json_exception(mock_session):
    mock_session.get.side_effect = Exception("Bob has raised an exception")
    result = await fetch_json(mock_session, "http://example.com/exception")
    assert result is None


@pytest.mark.asyncio
async def test_extract_product_with_prices():
    session = MagicMock()

    product_response = AsyncMock()
    product_response.status = 200
    product_response.json.return_value = {"title": "fake"}

    prices_response = AsyncMock()
    prices_response.status = 200
    prices_response.json.return_value = {
        "US": {"USD": [
            {"date": "2025-01-01", "price_base": 1000, "price_final": 500}
        ]
        }
    }

    def mock_get(url):
        ctx = AsyncMock()
        ctx.__aenter__.return_value = product_response if "product.json" in url else prices_response
        return ctx

    session.get = mock_get

    result = await extract_product(session, 123, usd_to_gbp=0.7)
    assert result["name"] == "fake"
    assert result["base_price_gbp_pence"] == 700
    assert result["final_price_gbp_pence"] == 350


@pytest.mark.asyncio
async def test_extract_product_missing_title():
    session = MagicMock()

    product_response = AsyncMock()
    product_response.status = 200
    product_response.json.return_value = {}

    def mock_get(*args):
        ctx = AsyncMock()
        ctx.__aenter__.return_value = product_response
        return ctx

    session.get = mock_get

    result = await extract_product(session, 123, usd_to_gbp=0.7)
    assert result is None


@pytest.mark.asyncio
async def test_extract_product_no_prices():
    session = MagicMock()

    product_response = AsyncMock()
    product_response.status = 200
    product_response.json.return_value = {"title": "Expedition 33"}

    prices_response = AsyncMock()
    prices_response.status = 200
    prices_response.json.return_value = {}

    def mock_get(url):
        ctx = AsyncMock()
        ctx.__aenter__.return_value = product_response if "product.json" in url else prices_response
        return ctx

    session.get = mock_get

    result = await extract_product(session, 123, usd_to_gbp=0.7)
    assert result["name"] == "Expedition 33"
    assert result["base_price_gbp_pence"] is None
    assert result["final_price_gbp_pence"] is None


@pytest.mark.asyncio
async def test_extract_batch():
    with patch(
        "extract_gog.extract_product",
        return_value={"id": 1}
    ) as mock_function:
        results = await extract_batch([1, 2, 3], usd_to_gbp=0.7)

    assert len(results) == 3
    assert mock_function.call_count == 3


def test_get_all_product_ids():
    html = """
            <html>
                <a href="123/">123/</a>
                <a href="invalidid/">invalidid/</a>
                <a href="456/">456/</a>
            </html>
    """

    mock_response = MagicMock()
    mock_response.text = html

    with patch("extract_gog.requests.get", return_value=mock_response):
        ids = get_all_product_ids()

    assert ids == [123, 456]
