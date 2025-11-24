"""Script which gets data from steam web api"""

import json
import os
from bs4 import BeautifulSoup
import requests

URL = 'https://store.steampowered.com/app/730/CounterStrike_2/'
FOLDER_PATH = 'data/'
FILEPATH = f'{FOLDER_PATH}steam_addon.json'


def get_data(url: str) -> str:
    """Function to obtain raw data from url html"""
    response = requests.get(url)
    raw_data = response.text
    if raw_data:
        return raw_data
    raise ValueError(
        f'{url} is invalid, leads to no match for the results_html label in the HTML page')


def convert_price(value: str) -> int:
    """Convert 'Free' to 0 and string nums to ints"""
    if value.isnumeric():
        return int(value)
    # if not numeric, assume free
    if value.lower() == 'free':
        return 0
    raise ValueError(f'Unexpected input: {value}')


def parse(data: str) -> list[dict]:
    """Function to scrape top selling games and output list of dicts with prices and titles"""
    games_list = []
    soup = BeautifulSoup(data, 'html.parser')

    games = soup.find_all("div", {"class": "game_purchase_price price"})
    for game in games:
        input(game.get_text().strip())
    if not games:
        raise ValueError(
            f'{data} contains no valid items with searched for tag)')

    for game in games:
        title = game.find('span', {'class': 'title'}).text
        latest_price = game.find(
            'div', {'class': 'discount_final_price'})
        if latest_price:
            latest_price = latest_price.text.strip().split(
                '£')[-1].replace('.', '')
        else:
            continue  # skip this game if no listed price
        try:
            price = game.find(
                'div', {'class': 'discount_original_price'}).text.strip().split('£')[-1].replace('.', '')
        except AttributeError:  # there is no discount, then .text attribute does not work
            price = latest_price

        extracted_game = {
            'name': title,
            'base_price_gbp_pence': convert_price(str(price)),
            'final_price_gbp_pence': convert_price(str(latest_price)),
        }

        games_list.append(extracted_game)

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

    game = get_data(URL)
    results.append(parse(game))

    # results = [game for list_of_50_games in results for game in list_of_50_games] # i miss you, list comp
    flattened_results = []
    for list_of_50_games in results:
        for game in list_of_50_games:
            flattened_results.append(game)

    output(flattened_results)


if __name__ == '__main__':
    export_steam()
