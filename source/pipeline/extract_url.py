"""Script which gets data from steam web api"""

import argparse
import re
import json
import os
from bs4 import BeautifulSoup
import requests


FOLDER_PATH = 'data/'  # needs to be /tmp/data for lambda
FILEPATH = f'{FOLDER_PATH}products.json'
STEAM_SEARCH = 'https://store.steampowered.com/search?term={search_term}'
STEAM_SPLIT = '<div class="search_name ellipsis">'
GOG_SEARCH = 'https://www.gog.com/en/games?query={search_term}&order=desc:score'
GOG_SPLIT = '<-product-tile _ngcontent-gogcom-store-c715558788"'
GOG_KEYWORDS = ["finalAmount", "baseAmount"]

# <--- Steam functions --->


def get_steam_html(search_input: str) -> str:
    """Get first result data from steam search term"""
    # build url
    response = requests.get(STEAM_SEARCH.format(search_term=search_input))
    raw_data = response.text
    if raw_data:
        # get the first result ignoring the headers
        raw_data = raw_data.split(STEAM_SPLIT)[1]
        return raw_data
    raise ValueError(
        f'{search_input} is invalid and leads to no match')


def convert_price(value: str) -> int:
    """Convert 'Free' to 0 and string nums to ints"""
    value = value.split('£')[-1].replace('.', '')
    if value.isnumeric():
        return int(value)
    # if not numeric, assume free
    if value.lower() == 'free':
        return 0
    raise ValueError(f'Unexpected input: {value}')


def parse_steam(data: str, search_input: str) -> dict:
    """Function to scrape top selling games and output list of dicts with prices and titles"""
    soup = BeautifulSoup(data, 'html.parser')

    # class = "discount_original_price" >£10.99 # if none, then no discount
    # class = "discount_final_price" >£10.99

    title = soup.find("span", {"class": "title"})
    if title:
        title = title.get_text().strip()
    else:
        raise ValueError(f'No search results found for {search_input}')

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
        'final_price_gbp_pence': convert_price(str(discount_price)),
        'platform': 'steam'
    }

    return listing


# <--- GOG functions --->


def get_gog_html(search_input: str) -> str:
    """Get first result data from search term"""
    # build url
    print(GOG_SEARCH.format(search_term=search_input))
    input()
    response = requests.get(GOG_SEARCH.format(search_term=search_input))
    raw_data = response.text
    if raw_data:
        raw_data = raw_data.split(GOG_SPLIT)[0]
        return raw_data
    raise ValueError(
        f'{search_input} is invalid and leads to no match')


# https://catalog.gog.com/v1/catalog?limit=48&query=like%3Astardew+valley


def get_gog_prices(search_input: str) -> dict:
    html = get_gog_html(search_input)
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find_all(
        'div', {"class": "product-tile__title ng-star-inserted"})
    input(title)

    final_amount = 'extract_amount(script_text, "finalAmount")'
    base_amount = 'extract_amount(script_text, "baseAmount")'

    listing = {
        'name': title,
        'base_price_gbp_pence': base_amount,
        'final_price_gbp_pence': final_amount,
        'platform': 'gog'
    }
    return listing

# <--- Main function --->


def output(results: list[dict]) -> None:
    """Function to create output json file"""
    if not os.path.isdir(FOLDER_PATH):
        os.mkdir(FOLDER_PATH)

    with open(FILEPATH, 'w+', encoding='utf-8') as f:
        json.dump(results, f, indent=4)


def export_games() -> None:

    os.makedirs(FOLDER_PATH, exist_ok=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search_input", default='stardew valley')
    args = parser.parse_args()
    user_input = args.search_input

    games_list = []

    # steam search
    game = get_steam_html(user_input)
    games_list.append(parse_steam(game, user_input))

    # gog search
    games_list.append(get_gog_prices(user_input))

    output(games_list)


if __name__ == '__main__':
    export_games()
