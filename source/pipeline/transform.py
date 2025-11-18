"""Script for transforming data for storage in RDS"""

import pandas as pd
import os
import json
from datetime import datetime


DIRECTORY = 'data/'
INPUT_PATH = f'{DIRECTORY}a_file.json'
INPUT_PATH = 'products.json'
OUTPUT_PATH = f'{DIRECTORY}clean_data.csv'
# list dict, product id, name, base price, retail, final price

# game
# listing - + GoG_id
# platform - + Gog
# price_record - + all data + current date


def divide_folders(file: str) -> pd.DataFrame:
    """Used to get data from a nested dict. Will return None if any level isn't valid"""

    price_record_df = pd.DataFrame()
    games = pd.DataFrame()
    platforms = pd.DataFrame()
    listings = pd.DataFrame()


if __name__ == "__main__":
    with open(INPUT_PATH) as f:
        gog_data = json.load(f)

    input(divide_folders(INPUT_PATH))
