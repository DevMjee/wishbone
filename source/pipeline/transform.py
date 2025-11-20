"""Script for transforming data for storage in RDS"""

import json
import os
from datetime import datetime
import pandas as pd


DIRECTORY = 'data/'
SOURCE_FILES = ['gog_products.json', 'steam_products.json']
OUTPUT_PATH = f'{DIRECTORY}clean_data.json'
TEST_DATA = 'test_products.json'


def transform_source(filename: str) -> pd.DataFrame:
    """
    Reads data from a JSON file into a Pandas dataframe
    and transforms it to the format expected by load script
    """
    # Read data from file
    with open(f'{DIRECTORY}{filename}', 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    # Create dataframe
    source_dataframe = pd.DataFrame(source_data)

    # Drop NaN values
    source_dataframe.dropna(subset=['base_price_gbp_pence'], inplace=True)

    # Create boolean series to check which values to calculate discount for (avoid dividing by 0)
    valid = source_dataframe["base_price_gbp_pence"] > 0

    # Calculate discount percentage
    source_dataframe["discount_percent"] = (
        (1 - source_dataframe["final_price_gbp_pence"] /
         source_dataframe["base_price_gbp_pence"]) * 100
    ).where(valid).round().astype("Int64")

    # Fill NaN values in discount percentage with zero
    source_dataframe.loc[:, 'discount_percent'] = source_dataframe['discount_percent'].fillna(
        0)

    # Redefine dataframe with relevant columns
    source_dataframe = source_dataframe[['name', 'base_price_gbp_pence',
                                         'final_price_gbp_pence', 'discount_percent']].copy()

    # Set platform name for all rows based on which file is being read
    # (e.g. reading from gog_products.json sets platform_name to 'gog')
    source_dataframe.loc[:, 'platform_name'] = filename.split('_')[0]

    # Timestamp data with today's date
    source_dataframe.loc[:, 'listing_date'] = datetime.today().date()

    # Cast prices to integers
    source_dataframe['base_price_gbp_pence'] = source_dataframe['base_price_gbp_pence'].astype(
        'Int64')

    source_dataframe['final_price_gbp_pence'] = source_dataframe['final_price_gbp_pence'].astype(
        'Int64')

    # Cast listing date to string
    source_dataframe['listing_date'] = source_dataframe['listing_date'].astype(
        'string')

    # Rename and reorder columns to be in line with load script input
    source_dataframe.rename(columns={'name': 'game_name',
                                     'base_price_gbp_pence': 'retail_price',
                                     'final_price_gbp_pence': 'final_price'}, inplace=True)

    source_dataframe = source_dataframe[['game_name', 'retail_price', 'platform_name',
                                         'listing_date', 'discount_percent', 'final_price']].copy()

    return source_dataframe


def transform_all():
    """Iterates through available sources and transforms raw data from them, saving to JSON"""
    # Check for data folder
    if not os.path.exists(DIRECTORY):
        raise FileNotFoundError("'data/' directory does not exist")

    # Get dataframes from each source and append to list
    all_data_sources = []
    for source_filename in SOURCE_FILES:
        all_data_sources.append(transform_source(source_filename))

    # Concatenate all source dataframes into one
    all_data = pd.concat(all_data_sources)

    # Export all data to json output
    all_data.to_json(
        OUTPUT_PATH, indent=4, lines=False, orient='records', mode='w')


if __name__ == "__main__":
    transform_all()
