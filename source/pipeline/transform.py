"""Script for transforming data for storage in RDS"""

import pandas as pd
import os
import json
from datetime import datetime


DIRECTORY = 'data/'
INPUT_PATH = f'{DIRECTORY}products.json'
OUTPUT_PATH = f'{DIRECTORY}clean_data.json'


def get_data(path: str) -> list[dict]:
    pass


def transform_gog(file: str) -> pd.DataFrame:
    # Read data from file
    with open(file) as f:
        gog_data = json.load(f)

    # Create dataframe
    all_data = pd.DataFrame(gog_data)

    # Drop NaN values
    all_data.dropna(subset=['base_price_gbp_pence'], inplace=True)

    # Create boolean series to check which values to calculate discount for (avoid dividing by 0)
    valid = (all_data["base_price_gbp_pence"] > 0) & \
            (all_data["final_price_gbp_pence"] > 0)

    # Calculate discount percentage
    all_data["discount_percent"] = (
        (1 - all_data["final_price_gbp_pence"] /
         all_data["base_price_gbp_pence"]) * 100
    ).where(valid).round().astype("Int64")

    # Fill NaN values in discount percentage with zero
    all_data.loc[:, 'discount_percent'] = all_data['discount_percent'].fillna(
        0)

    # Redefine dataframe with relevant columns
    all_data = all_data[['name', 'base_price_gbp_pence',
                         'final_price_gbp_pence', 'discount_percent']].copy()

    # Set platform name for all rows
    all_data.loc[:, 'platform_name'] = 'gog'

    # Timestamp data with today's date
    all_data.loc[:, 'listing_date'] = datetime.today().date()

    # Cast prices to integers
    all_data['base_price_gbp_pence'] = all_data['base_price_gbp_pence'].astype(
        'Int64')

    all_data['final_price_gbp_pence'] = all_data['final_price_gbp_pence'].astype(
        'Int64')

    # Cast listing date to string
    all_data['listing_date'] = all_data['listing_date'].astype('string')

    # Rename and reorder columns to be in line with load script input
    all_data.rename(columns={'name': 'game_name',
                    'base_price_gbp_pence': 'retail_price', 'final_price_gbp_pence': 'final_price'}, inplace=True)

    all_data = all_data[['game_name', 'retail_price', 'platform_name',
                         'listing_date', 'discount_percent', 'final_price']].copy()

    return all_data


if __name__ == "__main__":
    cleaned_data = transform_gog(INPUT_PATH)
    cleaned_data.to_json(OUTPUT_PATH, indent=4, orient='records')
