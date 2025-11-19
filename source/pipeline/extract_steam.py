"""Script which gets data from steam web api"""

import json
import os
from bs4 import BeautifulSoup
import requests

URL = 'https://store.steampowered.com/search/results/?query&start={start}&filter=topsellers&infinite=1'
INITIAL_URL = URL.format(start=0)
FOLDER_PATH = 'data/'
FILEPATH = f'{FOLDER_PATH}steam_products.json'
MAX_SEARCH = 500  # use totalresults(INITIAL_URL) when scaling up


def total_results(url):
    """Function to grap the total number of pages for possible data endpoints"""
    response = requests.get(url)
    raw_data = dict(response.json())
    results_count = raw_data['total_count']
    return int(results_count)


def get_data(url):
    """Function to obtain raw data from url html"""
    response = requests.get(url)
    raw_data = dict(response.json())
    return raw_data['results_html']


def convert_price(value: str) -> int:
    """Convert 'Free' to 0 and string nums to ints"""
    if value.isnumeric():
        return int(value)
    # if not numeric, assume free
    return 0


def parse(data):
    """Function to scrape top selling games and output list of dicts with prices and titles"""
    games_list = []
    soup = BeautifulSoup(data, 'html.parser')
    games = soup.find_all('a')

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
        except:
            price = latest_price

        if price == 'Free':
            price = 0

        extracted_game = {
            'name': title,
            'base_price_gbp_pence': convert_price(str(price)),
            'final_price_gbp_pence': convert_price(str(latest_price)),
        }

        games_list.append(extracted_game)

    return games_list


def output(results) -> None:
    """Function to create output json file"""
    if not os.path.isdir(FOLDER_PATH):
        os.mkdir(FOLDER_PATH)

    with open(FILEPATH, 'w+') as f:
        json.dump(results, f, indent=4)


if __name__ == '__main__':
    results = []

    for step in range(0, MAX_SEARCH, 50):
        top_selling = get_data(URL.format(start=step))
        results.append(parse(top_selling))
        print('Results Scraped: ', step)

    output(results)
