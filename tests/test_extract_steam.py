"""Tests for the extract_steam script"""

import pytest
from source.pipeline.extract_steam import get_total_page_count, get_data, convert_price, parse


def test_convert_price_valid_1():
    assert convert_price('Free') == 0


def test_convert_price_valid_3():  # check case insensitive
    assert convert_price('free') == 0


def test_convert_price_valid_2():
    assert convert_price('900') == 900


def test_convert_price_invalid_1():
    with pytest.raises(ValueError):
        convert_price('random_string')


def test_total_results_invalid_1():
    with pytest.raises(ValueError):
        get_total_page_count('invalid_url')


def test_get_data_invalid_1():
    with pytest.raises(ValueError):
        get_data('invalid_url')


def test_parse_invalid_1():
    with pytest.raises(ValueError):
        parse('invalid_data')
