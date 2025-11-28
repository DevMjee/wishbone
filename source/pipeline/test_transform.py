import json
from pathlib import Path
from datetime import date
from unittest.mock import patch, mock_open
import pytest
import pandas as pd

from transform import (
    read_data,
    calculate_discount,
    cast_to_int,
    get_relevant_columns,
    reorder_columns,
    transform_source,
)


def test_read_data_reads_json_correctly(tmp_path):
    data = [{"a": 1}, {"a": 2}]
    file_path = tmp_path / "test.json"
    file_path.write_text(json.dumps(data))

    with patch("transform.DIRECTORY", str(tmp_path) + "/"):
        result = read_data("test.json")

    assert result == data


def test_calculate_discount_basic():
    df = pd.DataFrame({
        "base_price_gbp_pence": [1000, 2000],
        "final_price_gbp_pence": [500, 1000]
    })

    result = calculate_discount(df)

    assert list(result["discount_percent"]) == [50, 50]


def test_calculate_discount_zero_base_price():
    df = pd.DataFrame({
        "base_price_gbp_pence": [0, 1000],
        "final_price_gbp_pence": [500, 500]
    })

    result = calculate_discount(df)

    assert pd.isna(result["discount_percent"].iloc[0])
    assert result["discount_percent"].iloc[1] == 50


def test_calculate_discount_missing_column():
    df = pd.DataFrame({
        "base_price_gbp_pence": [1000, 2000]
    })
    with pytest.raises(KeyError):
        calculate_discount(df)


def test_cast_to_int_success():
    df = pd.DataFrame({
        "base_price_gbp_pence": [1000, 2000],
        "final_price_gbp_pence": [900, 1500]
    })
    result = cast_to_int(df)

    assert str(result["base_price_gbp_pence"].dtype) == "Int64"
    assert str(result["final_price_gbp_pence"].dtype) == "Int64"


def test_cast_to_int_failure():
    df = pd.DataFrame({
        "base_price_gbp_pence": ["abc", 2000],
        "final_price_gbp_pence": [900, 1500]
    })
    with pytest.raises(ValueError):
        cast_to_int(df)


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "name": ["Game A", "Game B"],
        "base_price_gbp_pence": [1000, 2000],
        "final_price_gbp_pence": [500, 1500],
        "discount_percent": [None, None]
    })


def test_get_relevant_columns(sample_dataframe):
    result = get_relevant_columns(sample_dataframe)

    assert list(result.columns) == [
        "name",
        "base_price_gbp_pence",
        "final_price_gbp_pence",
        "discount_percent",
    ]


def test_reorder_columns(sample_dataframe):
    df = sample_dataframe.copy()
    df["platform_name"] = "gog"
    df["listing_date"] = str(date.today())

    result = reorder_columns(df)

    assert list(result.columns) == [
        "game_name",
        "retail_price",
        "platform_name",
        "listing_date",
        "discount_percent",
        "final_price"
    ]


def test_transform_source_general():
    # JSON returned by read_data()
    fake_json = [
        {
            "name": "Game A",
            "base_price_gbp_pence": 1000,
            "final_price_gbp_pence": 500
        },
        {
            "name": "Game B",
            "base_price_gbp_pence": None,  # should be dropped
            "final_price_gbp_pence": 300
        }
    ]

    m = mock_open(read_data="dummy")

    with patch("transform.open", m):
        with patch("transform.json.load", return_value=fake_json):
            df = transform_source("gog_products.json")

    expected = pd.DataFrame([
        {
            "game_name": "Game A",
            "retail_price": 1000,
            "platform_name": "gog",
            "listing_date": df["listing_date"].iloc[0],
            "discount_percent": 50,
            "final_price": 500,
        }
    ])

    pd.testing.assert_frame_equal(df.reset_index(
        drop=True), expected, check_dtype=False)


def test_transform_source_with_tmpfile(tmp_path):
    data = [
        {"name": "Game X", "base_price_gbp_pence": 1000,
            "final_price_gbp_pence": 500},
        {"name": "Game Y", "base_price_gbp_pence": 2000,
            "final_price_gbp_pence": 1500},
    ]

    filepath = tmp_path / "gog_products.json"
    filepath.write_text(json.dumps(data))

    with patch("transform.DIRECTORY", str(tmp_path) + "/"):
        df = transform_source("gog_products.json")

    assert len(df) == 2
    assert "game_name" in df.columns
    assert df.iloc[0]["platform_name"] == "gog"
