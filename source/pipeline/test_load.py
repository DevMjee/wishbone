"""Tests for load script"""

from unittest.mock import MagicMock, patch, mock_open
from datetime import date
from load import get_or_create_game, get_or_create_platform, insert_listing, load_data, get_connection


def test_get_create_game_existing_1():
    cur = MagicMock()
    cur.fetchone.return_value = (10,)

    result = get_or_create_game(cur, "Expedition 33", 4000)

    cur.execute.assert_called_once()
    assert result == 10


def test_get_create_game_existing_2():
    cur = MagicMock()
    cur.fetchone.return_value = (10,)

    result = get_or_create_game(cur, "The Witcher 3", 2500)

    cur.execute.assert_called_once()
    assert result == 10


def test_get_create_game_existing_3():
    cur = MagicMock()
    cur.fetchone.return_value = (10,)

    result = get_or_create_game(cur, "Trackmania", 0)

    cur.execute.assert_called_once()
    assert result == 10


def test_get_or_create_game_insert_1():
    cur = MagicMock()

    cur.fetchone.side_effect = [None, (77,)]

    result = get_or_create_game(cur, "Expedition 1", 4000)

    assert result == 77
    assert cur.execute.call_count == 2


def test_get_or_create_game_insert_2():
    cur = MagicMock()

    cur.fetchone.side_effect = [None, (77,)]

    result = get_or_create_game(cur, "The Witcher 70", 40000)

    assert result == 77
    assert cur.execute.call_count == 2


def test_get_or_create_game_insert_3():
    cur = MagicMock()

    cur.fetchone.side_effect = [None, (77,)]

    result = get_or_create_game(cur, "Trackmania 3", 50000)

    assert result == 77
    assert cur.execute.call_count == 2


def test_get_create_platform_existing_1():
    cur = MagicMock()
    cur.fetchone.return_value = (1,)

    result = get_or_create_platform(cur, "steam")

    cur.execute.assert_called_once()
    assert result == 1


def test_get_create_platform_existing_2():
    cur = MagicMock()
    cur.fetchone.return_value = (1,)

    result = get_or_create_platform(cur, "gog")

    cur.execute.assert_called_once()
    assert result == 1


def test_get_create_platform_existing_3():
    cur = MagicMock()
    cur.fetchone.return_value = (1,)

    result = get_or_create_platform(cur, "epic")

    cur.execute.assert_called_once()
    assert result == 1


def test_get_create_platform_insert_1():
    cur = MagicMock()
    cur.fetchone.side_effect = [None, (9,)]

    result = get_or_create_platform(cur, "steam")

    assert result == 9
    assert cur.execute.call_count == 2


def test_get_create_platform_insert_2():
    cur = MagicMock()
    cur.fetchone.side_effect = [None, (3,)]

    result = get_or_create_platform(cur, "gog")

    assert result == 3
    assert cur.execute.call_count == 2


def test_get_create_platform_insert_3():
    cur = MagicMock()
    cur.fetchone.side_effect = [None, (5,)]

    result = get_or_create_platform(cur, "epic")

    assert result == 5
    assert cur.execute.call_count == 2


def test_insert_listing_calls_execute_1():
    cur = MagicMock()
    insert_listing(cur, 4, 2, 5000, 50, date(2025, 2, 4))

    cur.execute.assert_called_once()
    _, params = cur.execute.call_args[0]
    assert params == (4, 2, 5000, 50, date(2025, 2, 4))


def test_insert_listing_calls_execute_2():
    cur = MagicMock()
    insert_listing(cur, 6, 90, 1000, 90, date(2023, 8, 9))

    cur.execute.assert_called_once()
    _, params = cur.execute.call_args[0]
    assert params == (6, 90, 1000, 90, date(2023, 8, 9))


def test_insert_listing_calls_execute_3():
    cur = MagicMock()
    insert_listing(cur, 7, 25, 8000, 20, date(2024, 3, 3))

    cur.execute.assert_called_once()
    _, params = cur.execute.call_args[0]
    assert params == (7, 25, 8000, 20, date(2024, 3, 3))


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
