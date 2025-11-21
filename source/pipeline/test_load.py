"""Tests for load script"""

from unittest.mock import MagicMock, patch, mock_open
from datetime import date
from load import get_or_create_game, get_or_create_platform, insert_listing, load_data, get_connection


def test_get_create_game_existing():
    cur = MagicMock()
    cur.fetchone.return_value = (10,)

    result = get_or_create_game(cur, "Expedition 33", 4000)

    cur.execute.assert_called_once()
    assert result == 10


def test_get_or_create_game_insert():
    cur = MagicMock()

    cur.fetchone.side_effect = [None, (77,)]

    result = get_or_create_game(cur, "Expedition 1", 4000)

    assert result == 77
    assert cur.execute.call_count == 2


def test_get_create_platform_existing():
    cur = MagicMock()
    cur.fetchone.return_value = (1,)

    result = get_or_create_platform(cur, "steam")

    cur.execute.assert_called_once()
    assert result == 1


def test_get_create_platform_insert():
    cur = MagicMock()
    cur.fetchone.side_effect = [None, (2,)]

    result = get_or_create_platform(cur, "gog")

    assert result == 2
    assert cur.execute.call_count == 2


def test_insert_listing_calls_execute():
    cur = MagicMock()
    insert_listing(cur, 1, 2, 1000, 50, date(2025, 1, 1))

    cur.execute.assert_called_once()
    _, params = cur.execute.call_args[0]
    assert params == (1, 2, 1000, 50, date(2025, 1, 1))


@patch("load.open", new_callable=mock_open, read_data="[]")
@patch("load.json.load")
@patch("load.get_connection")
def test_load_data_success(mock_conn_function, mock_json_load, mock_open_file):
    mock_json_load.return_value = [{
        "game_name": "Bob",
        "retail_price": 5000,
        "platform_name": "steam",
        "listing_date": "2025-01-01",
        "discount_percent": 50,
        "price": 2000
    }]

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn_function.return_value = mock_conn

    mock_cursor.fetchone.side_effect = [None, (1,), None, (5,)]

    load_data()

    assert mock_conn.commit.call_count == 1
    assert mock_cursor.close.called
    assert mock_conn.close.called


@patch("load.open", new_callable=mock_open, read_data="[]")
@patch("load.json.load")
@patch("load.get_connection")
def test_load_data_error(mock_conn_function, mock_json_load, mock_open_file):
    mock_json_load.return_value = [{
        "game_name": "Bob",
        "retail_price": 5000,
        "platform_name": "steam",
        "listing_date": "2025-01-01",
        "discount_percent": 50,
        "price": 2000
    }]

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("DB error")
    mock_conn.cursor.return_value = mock_cursor
    mock_conn_function.return_value = mock_conn

    load_data()

    mock_conn.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
