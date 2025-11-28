"""Script for transforming data for storage in RDS"""

import json
from datetime import date, timedelta
import pandas as pd


DIRECTORY = '/var/task/tmp/data/'
SOURCE_FILES = ['gog_products.json', 'steam_products.json']
OUTPUT_PATH = f'{DIRECTORY}clean_data.json'
TEST_DATA = 'test_products.json'
TODAY = date.today()
# for testing historical pipeline deletion
YESTERDAY = TODAY - timedelta(days=1)
# TODAY = YESTERDAY
# ggg


def read_data(filename: str) -> list[dict]:
    """Returns the JSON in source file as a list of dictionaries"""
    with open(f'{DIRECTORY}{filename}', 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_discount(data: pd.DataFrame) -> pd.DataFrame:
    """Calculates the percentage discount as a column"""
    valid = data["base_price_gbp_pence"] > 0

    data["discount_percent"] = (
        (1 - data["final_price_gbp_pence"] /
         data["base_price_gbp_pence"]) * 100
    ).where(valid).round().astype("Int64")

    return data


def cast_to_int(data: pd.DataFrame) -> pd.DataFrame:
    data['base_price_gbp_pence'] = data['base_price_gbp_pence'].astype(
        'Int64')

    data['final_price_gbp_pence'] = data['final_price_gbp_pence'].astype(
        'Int64')

    return data


def reorder_columns(data: pd.DataFrame) -> pd.DataFrame:
    data.rename(columns={'name': 'game_name',
                         'base_price_gbp_pence': 'retail_price',
                         'final_price_gbp_pence': 'final_price'}, inplace=True)

    data = data[['game_name', 'retail_price', 'platform_name',
                 'listing_date', 'discount_percent', 'final_price']].copy()

    return data


def get_relevant_colummns(data: pd.DataFrame) -> pd.DataFrame:
    data = data[['name', 'base_price_gbp_pence',
                 'final_price_gbp_pence', 'discount_percent']].copy()

    return data


def transform_source(filename: str) -> pd.DataFrame:
    """
    Reads data from a JSON file into a Pandas dataframe
    and transforms it to the format expected by load script
    """
    # Read data from file
    source_data = read_data(filename)

    # Create dataframe
    source_dataframe = pd.DataFrame(source_data)

    # Drop NaN values
    source_dataframe.dropna(subset=['base_price_gbp_pence'], inplace=True)

    # Calculate discount percentages
    source_dataframe = calculate_discount(source_dataframe)

    # Fill NaN values in discount percentage with zero
    source_dataframe.loc[:, 'discount_percent'] = source_dataframe['discount_percent'].fillna(
        0)

    # Redefine dataframe with relevant columns
    source_dataframe = get_relevant_colummns(source_dataframe)

    # Set platform name for all rows based on which file is being read
    # (e.g. reading from gog_products.json sets platform_name to 'gog')
    source_dataframe.loc[:, 'platform_name'] = filename.split('_')[0]

    # Timestamp data with today's date
    source_dataframe.loc[:, 'listing_date'] = TODAY

    # Cast prices to integers
    source_dataframe = cast_to_int(source_dataframe)

    # Cast listing date to string
    source_dataframe['listing_date'] = source_dataframe['listing_date'].astype(
        'string')

    # Rename and reorder columns to be in line with load script input
    source_dataframe = reorder_columns(source_dataframe)

    return source_dataframe


def transform_all():
    """Iterates through available sources and transforms raw data from them, saving to JSON"""
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
