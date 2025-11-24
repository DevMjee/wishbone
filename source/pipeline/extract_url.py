"""Script which gets data from steam web api"""

import json
import os
from bs4 import BeautifulSoup
import requests

URL = 'https://store.steampowered.com/app/1817070/Marvels_SpiderMan_Remastered/'
URL = 'https://store.steampowered.com/app/632360/Risk_of_Rain_2/'
URL = 'https://store.steampowered.com/app/80/CounterStrike_Condition_Zero/'
URL = 'https://store.steampowered.com/app/730/CounterStrike_2/'

#  user gives url, we find other url from this,

FOLDER_PATH = 'data/'  # needs to be /tmp/data for lambda
FILEPATH = f'{FOLDER_PATH}steam_addon.json'
SEARCH_TERM = 'stardew valley'  # user given
SEARCH_TERM = 'spiderman'  # user given
STEAM_SEARCH = 'https://store.steampowered.com/search?term={search_term}'


def get_data() -> str:
    """Get data from search term"""
    # build url
    response = requests.get(STEAM_SEARCH.format(search_term=SEARCH_TERM))
    raw_data = response.text
    if raw_data:
        return raw_data
    raise ValueError(
        f'{SEARCH_TERM} is invalid and leads to no match')


def convert_price(value: str) -> int:
    """Convert 'Free' to 0 and string nums to ints"""
    if value.isnumeric():
        return int(value)
    # if not numeric, assume free
    if value.lower() == 'free':
        return 0
    raise ValueError(f'Unexpected input: {value}')


def parse_steam(data: str) -> list[dict]:
    """Function to scrape top selling games and output list of dicts with prices and titles"""
    games_list = []
    soup = BeautifulSoup(data, 'html.parser')

    #  removes 'On Steam' from title
    title = soup.title.string.strip()[:-9]
    input(title)
    # class = "discount_original_price" >£10.99 # if none, then no discount
    # class = "discount_final_price" >£10.99

    original_price = soup.find(
        "div", {"class": "discount_original_price"})

    if original_price:  # if on discount
        original_price = original_price.get_text().strip()
        discount_price = soup.find(
            "div", {"class": "discount_final_price"}).get_text().strip()

    else:  #  not on discount
        price = soup.find(
            "div", {"class": "game_purchase_price price"}).get_text().strip()

    return games_list


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
    game_data = parse_steam(game)

    output(game_data)


if __name__ == '__main__':
    export_steam()
