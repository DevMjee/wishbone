"""Script which gets data from steam web api"""

import re
import json
import os
from bs4 import BeautifulSoup
import requests


FOLDER_PATH = 'data/'  # needs to be /tmp/data for lambda
FILEPATH = f'{FOLDER_PATH}steam_addon.json'
SEARCH_TERM = 'stardew valley'  # user given
STEAM_SEARCH = 'https://store.steampowered.com/search?term={search_term}'
SEARCH_SPLIT = '<div class="search_name ellipsis">'


def get_data() -> str:
    """Get first result data from search term"""
    # build url
    response = requests.get(STEAM_SEARCH.format(search_term=SEARCH_TERM))
    raw_data = response.text
    if raw_data:
        # get the first result ignoring the headers
        raw_data = raw_data.split(SEARCH_SPLIT)[1]
        return raw_data
    raise ValueError(
        f'{SEARCH_TERM} is invalid and leads to no match')


def convert_price(value: str) -> int:
    """Convert 'Free' to 0 and string nums to ints"""
    value = value.split('£')[-1].replace('.', '')
    if value.isnumeric():
        return int(value)
    # if not numeric, assume free
    if value.lower() == 'free':
        return 0
    raise ValueError(f'Unexpected input: {value}')


def parse_steam(data: str) -> list[dict]:
    """Function to scrape top selling games and output list of dicts with prices and titles"""
    soup = BeautifulSoup(data, 'html.parser')

    # class = "discount_original_price" >£10.99 # if none, then no discount
    # class = "discount_final_price" >£10.99

    title = soup.find("span", {"class": "title"})
    if title:
        title = title.get_text().strip()
    else:
        raise ValueError(f'No search results found for {SEARCH_TERM}')

    discount_price = soup.find(
        "div", {"class": "discount_final_price"})
    if discount_price:
        discount_price = discount_price.get_text().strip()
    else:
        raise ValueError(
            'Uh oh. Steam must have changed how they label discount prices!')

    original_price = soup.find(
        "div", {"class": "discount_original_price"})
    if original_price:  # if on discount
        original_price = original_price.get_text().strip()
    else:  #  not on discount
        original_price = discount_price

    listing = {
        'name': title,
        'base_price_gbp_pence': convert_price(str(original_price)),
        'final_price_gbp_pence': convert_price(str(discount_price))
    }
    input(listing)


def output(results: list[dict]) -> None:
    """Function to create output json file"""
    if not os.path.isdir(FOLDER_PATH):
        os.mkdir(FOLDER_PATH)

    with open(FILEPATH, 'w+', encoding='utf-8') as f:
        json.dump(results, f, indent=4)


def export_steam() -> None:
    results = []

    os.makedirs(FOLDER_PATH, exist_ok=True)

    game = get_data()
    print(game)
    game_data = parse_steam(game)

    output(game_data)


if __name__ == '__main__':
    export_steam()
