"""Tests for historical pipeline script"""

from datetime import date
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
from source.s3_pipeline.historical_pipeline import extract_table, transform_listing, load_dim_table, load_listing_partitioned, delete_old_listing_data, main, lambda_handler


def test_extract_table_valid():
    fake_engine = MagicMock()
    fake_conn = MagicMock()
    fake_engine.begin.return_value.__enter__.return_value = fake_conn

    with patch("source.s3_pipeline.historical_pipeline.get_engine", return_value=fake_engine), patch("pandas.read_sql", return_value=pd.DataFrame({"id": [1, 2]})) as mock_read_sql:
        df = extract_table("game")

        mock_read_sql.assert_called_once()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2


def test_extract_table_invalid():
    with pytest.raises(ValueError):
        extract_table("bob")


def test_transforming_listing():
    df = pd.DataFrame({"recording_date": ["2025-01-01", "2025-01-02"]})

    df_transformed = transform_listing(df)

    assert isinstance(df_transformed["recording_date"].iloc[0], date)
    assert df_transformed["recording_date"].iloc[0] == date(2025, 1, 1)


def test_load_dim_table_append():
    df = pd.DataFrame({"id": [1]})

    with patch("awswrangler.s3.does_object_exist", return_value=True), patch("awswrangler.s3.to_parquet") as mock_parquet:
        load_dim_table(df, "s3://bucket/game.parquet")

        _, kwargs = mock_parquet.call_args
        assert kwargs["mode"] == "append"
        assert kwargs["dataset"] is True


def test_load_dim_table_overwrite():
    df = pd.DataFrame({"id": [1]})

    with patch("awswrangler.s3.does_object_exist", return_value=False), patch("awswrangler.s3.to_parquet") as mock_parquet:
        load_dim_table(df, "s3://bucket/game.parquet")

        _, kwargs = mock_parquet.call_args
        assert kwargs["mode"] == "overwrite"


def test_load_listing_partitioned():
    df = pd.DataFrame({"recording_date": ["2025-03-04"]})

    with patch("awswrangler.s3.to_parquet") as mock_parquet:
        load_listing_partitioned(df)

        mock_parquet.assert_called_once()
        _, kwargs = mock_parquet.call_args
        assert kwargs["partition_cols"] == ["year", "month", "day"]


def test_delete_old_listing_data():
    fake_conn = MagicMock()
    fake_result = MagicMock()
    fake_result.rowcount = 5
    fake_conn.execute.return_value = fake_result

    fake_engine = MagicMock()
    fake_engine.begin.return_value.__enter__.return_value = fake_conn

    with patch("source.s3_pipeline.historical_pipeline.get_engine", return_value=fake_engine):
        delete_old_listing_data()

        fake_conn.execute.assert_called_once()
        assert "today" in fake_conn.execute.call_args[0][1]


def test_main():
    with patch("source.s3_pipeline.historical_pipeline.extract_table") as mock_extract, \
            patch("source.s3_pipeline.historical_pipeline.transform_listing") as mock_transform, \
            patch("source.s3_pipeline.historical_pipeline.load_dim_table") as mock_dim, \
            patch("source.s3_pipeline.historical_pipeline.load_listing_partitioned") as mock_listing, \
            patch("source.s3_pipeline.historical_pipeline.delete_old_listing_data") as mock_delete:

        main()

        assert mock_extract.call_count == 3
        mock_transform.assert_called_once()
        assert mock_dim.call_count == 2
        mock_listing.assert_called_once()
        mock_delete.assert_called_once()


def test_lambda_handler():
    with patch("source.s3_pipeline.historical_pipeline.main") as mock_main:
        response = lambda_handler({}, {})

        mock_main.assert_called_once()
        assert response == {"status": "success",
                            "msg": "Historical pipeline completed"}
