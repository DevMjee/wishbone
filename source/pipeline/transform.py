"""Script for transforming data for storage in RDS"""

import pandas as pd
import os
import json
from datetime import datetime


DIRECTORY = 'data/'
# INPUT_PATH = f'{DIRECTORY}a_file.json'
INPUT_PATH = 'products.json'
OUTPUT_PATH = f'{DIRECTORY}clean_data.json'
# list dict, product id, name, base price, retail, final price

# game
# listing - + GoG_id
# platform - + Gog
# price_record - + all data + current date


def transform_gog(file: str) -> pd.DataFrame:
    """Used to get data from a nested dict. Will return None if any level isn't valid"""
    with open(file) as f:
        gog_data = json.load(f)

    all_data = pd.DataFrame(gog_data)

    all_data.dropna(subset=['base_price_gbp_pence'], inplace=True)

    valid = (all_data["base_price_gbp_pence"] > 0) & \
            (all_data["final_price_gbp_pence"] > 0)

    all_data["discount_percent"] = (
        (1 - all_data["final_price_gbp_pence"] /
         all_data["base_price_gbp_pence"]) * 100
    ).where(valid).round().astype("Int64")

    all_data.loc[:, 'discount_percent'] = all_data['discount_percent'].fillna(
        0)

    all_data = all_data[['name', 'base_price_gbp_pence',
                         'final_price_gbp_pence', 'discount_percent']].copy()

    all_data.loc[:, 'platform_name'] = 'gog'

    all_data.loc[:, 'listing_date'] = datetime.today().date()

    all_data['base_price_gbp_pence'] = all_data['base_price_gbp_pence'].astype(
        'Int64')

    all_data['final_price_gbp_pence'] = all_data['final_price_gbp_pence'].astype(
        'Int64')

    all_data['listing_date'] = all_data['listing_date'].astype('string')

    all_data.rename(columns={'name': 'game_name',
                    'base_price_gbp_pence': 'retail_price', 'final_price_gbp_pence': 'final_price'}, inplace=True)

    all_data = all_data[['game_name', 'retail_price', 'platform_name',
                         'listing_date', 'discount_percent', 'final_price']].copy()

    return all_data


if __name__ == "__main__":
    cleaned_data = transform_gog(INPUT_PATH)
    cleaned_data.to_json(OUTPUT_PATH, indent=4, orient='records')
