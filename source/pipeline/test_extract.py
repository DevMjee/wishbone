"""Tests for the extract script"""


import pytest
import requests
from unittest.mock import patch

from extract import get_steam_html, get_gog_prices, get_gog_html, convert_price, parse_steam, extract_games, output


class APIClient:
    """Defines mock html response"""

    def get_data(self, url):
        response = requests.get(url)
        return response


@pytest.fixture
def mock_response():
    with patch('requests.get') as mock_get:
        yield mock_get


def test_convert_price_valid_1():
    assert convert_price('Free') == 0


def test_convert_price_valid_3():  # check case insensitive
    assert convert_price('free') == 0


def test_convert_price_valid_2():
    assert convert_price('900') == 900


def test_convert_price_invalid_1():
    with pytest.raises(ValueError):
        convert_price('random_string')


def test_get_steam_html_valid_2():
    # must be this, not False
    assert get_steam_html('qazwsxedcrfvtgbyhnujmikolp') == ''
    # note: this test fails if any game is created with this name
    # I believe this is unlikely
