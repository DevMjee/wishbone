"""Script which gets data from web api search console, one game at a time"""

import argparse
import re
import json
import os
from bs4 import BeautifulSoup
from forex_python.converter import CurrencyRates
import requests


FOLDER_PATH = 'data/'  # needs to be /tmp/data for lambda

STEAM_PATH = f'{FOLDER_PATH}steam_products.json'
STEAM_SEARCH = 'https://store.steampowered.com/search?term={search_term}'
STEAM_SPLIT = '<div class="search_name ellipsis">'

GOG_PATH = f'{FOLDER_PATH}gog_products.json'
GOG_SEARCH = 'https://catalog.gog.com/v1/catalog?limit=48&query=like%3A{search_term}'
DEFAULT_RATE = 0.77

# <--- Steam functions --->


def get_steam_html(search_input: str) -> str:
    """Get first result data from steam search term"""
    # build url
    response = requests.get(STEAM_SEARCH.format(search_term=search_input))
    raw_data = response.text
    raw_data = raw_data.split(STEAM_SPLIT)
    if len(raw_data) <= 1:
        print(f'{search_input} is invalid and leads to no match for Steam')
        return ''  # len = 1 means no search results found, return falsey value
    # else get the first result ignoring the headers
    return raw_data[1]


def parse_steam(data: str, search_input: str) -> dict:
    """Function to scrape top selling games and output list of dicts with prices and titles"""
    soup = BeautifulSoup(data, 'html.parser')

    # class = "discount_original_price" >£10.99 # if none, then no discount
    # class = "discount_final_price" >£10.99

    title = soup.find("span", {"class": "title"})
    if title:
        title = title.get_text().strip()
    else:
        return {}  # if no match

    discount_price = soup.find(
        "div", {"class": "discount_final_price"})
    if discount_price:
        discount_price = discount_price.get_text().strip()
    else:
        raise ValueError(
            'Have Steam have changed how they label discount prices?')

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

    return listing


# <--- GOG functions --->


def get_gog_html(search_input: str) -> dict:
    """Get first result data from search term"""
    # build url
    response = requests.get(GOG_SEARCH.format(search_term=search_input))
    raw_data = dict(response.json()).get('products')
    if raw_data:
        return raw_data[0]  # only the first match
    # else:
    print(f'{search_input} is invalid and leads to no match on GOG')
    return {}


def get_gog_prices(search_input: str, convert_rate: float = DEFAULT_RATE) -> dict:
    data = get_gog_html(search_input)
    title = data.get('title')
    if not title:  # no matches
        return {}

    prices = data.get('price')
    if not prices:
        raise ValueError('There are no prices here, oops')

    final_amount = prices.get('final')
    base_amount = prices.get('base')

    listing = {
        'name': title,
        'base_price_gbp_pence': convert_price(base_amount, convert_rate),
        'final_price_gbp_pence': convert_price(final_amount, convert_rate)
    }
    return listing

# <--- Main function --->


def convert_price(value: str, convert_rate: float = DEFAULT_RATE) -> int:
    """Convert 'Free' to 0 and string nums to ints"""
    if '$' in value:
        value = value.split('$')[-1].replace('.', '')
        if value.isnumeric():
            return int(int(value) * convert_rate)

    else:
        value = value.split('£')[-1].replace('.', '')

    if value.isnumeric():
        return int(value)
    # if not numeric, assume free
    if value.lower() == 'free':
        return 0
    raise ValueError(f'Unexpected input: {value}')


def output(results: dict, destination: str) -> None:
    """Function to create output json file"""
    if not results:
        print(f'no matches for {destination}')
        return

    if not os.path.isdir(FOLDER_PATH):
        os.mkdir(FOLDER_PATH)

    with open(destination, 'w+', encoding='utf-8') as f:
        json.dump(results, f, indent=4)


def export_games() -> None:

    os.makedirs(FOLDER_PATH, exist_ok=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search_input", default='stardew valley')
    args = parser.parse_args()
    user_input = args.search_input

    # steam search
    game = get_steam_html(user_input)
    output(parse_steam(game, user_input), STEAM_PATH)

    # gog search
    try:
        c = CurrencyRates()
        usd_to_gbp_rate = float(c.get_rate("USD", "GBP"))
    except:
        print("RatesNotAvailableError - Forex API is currently unavailable")
        usd_to_gbp_rate = DEFAULT_RATE

    output(get_gog_prices(user_input, usd_to_gbp_rate), GOG_PATH)


if __name__ == '__main__':
    export_games()
