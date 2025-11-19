import pytest
from unittest.mock import MagicMock, patch
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
    _, args = cur.execute.call_args
    assert args[1] == (1, 2, 1000, 50, date(2025, 1, 1))
