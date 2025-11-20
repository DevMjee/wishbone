from unittest.mock import patch, mock_open
import pandas as pd


def test_transform_source_general_source():
    # What json.load should return
    fake_json = [
        {
            "name": "Game A",
            "base_price_gbp_pence": 1000,
            "final_price_gbp_pence": 500
        },
        {
            "name": "Game B",
            "base_price_gbp_pence": None,
            "final_price_gbp_pence": 300
        }
    ]

    # Mock file contents (not used because json.load is mocked)
    m = mock_open(read_data="dummy")

    with patch("transform.open", m):
        with patch("transform.json.load", return_value=fake_json):
            from transform import transform_source

            df = transform_source("gog_products.json")

    # Validate resulting dataframe
    expected = pd.DataFrame([
        {
            "game_name": "Game A",
            "retail_price": 1000,
            "platform_name": "gog",
            "listing_date": df["listing_date"].iloc[0],  # today's date
            "discount_percent": 50,
            "final_price": 500,
        }
    ])

    pd.testing.assert_frame_equal(df.reset_index(
        drop=True), expected, check_dtype=False)
