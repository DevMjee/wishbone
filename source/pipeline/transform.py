"""Script for transforming data for storage in RDS"""

import pandas as pd
import os
import json
from datetime import datetime


DIRECTORY = 'data/'
GOG_INPUT_FILE = 'gog_products.json'
STEAM_INPUT_FILE = 'steam_products.json'
OUTPUT_PATH = f'{DIRECTORY}clean_data.json'


def transform_data(filename: str) -> pd.DataFrame:
    # Read data from file
    with open(f'{DIRECTORY}{filename}') as f:
        data = json.load(f)

    # Create dataframe
    all_data = pd.DataFrame(data)

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

    # Set platform name for all rows based on which file is being read
    # (e.g. reading from gog_products.json sets platform_name to 'gog')
    all_data.loc[:, 'platform_name'] = filename.split('_')[0]

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


def transform_all():
    # Transform GoG data
    transform_data(GOG_INPUT_FILE).to_json(
        OUTPUT_PATH, indent=4, orient='records')
    # Transform Steam data
    transform_data(STEAM_INPUT_FILE).to_json(
        OUTPUT_PATH, indent=4, orient='records')


if __name__ == "__main__":
    transform_all()
