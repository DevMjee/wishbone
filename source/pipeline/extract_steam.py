"""Script which gets data from steam web api"""
from os import environ
import requests
import multiprocessing
import time
import json
import numpy as np
import pandas as pd

URL_FORMAT = "https://store.steampowered.com/api/appdetails/?appids={app_ids}&cc=uk"
# for boolean checking
PRICE_FORMAT = "https://store.steampowered.com/api/appdetails/?appids={app_id}&cc=uk"

# WISHLIST_URL_FORMAT = "https://api.steampowered.com/IWishlistService/GetWishlist/v1/?access_token={api_key}&steamid={steamid}"
MAX_RESULTS = 100
NUM_PROCESSES_INFO = 16
NUM_PROCESSES_PRICE = 64


def get_from_db(app_ids: list[int]) -> dict:
    """Pull games, ids, and prices from api"""
    app_ids = [str(app_id) for app_id in app_ids]
    app_ids_csv = ','.join(app_ids)
    # print(app_ids_csv)
    response = requests.get(URL_FORMAT.format(app_ids=app_ids_csv))
    # response_list = [{k: v} for k, v in response.json().items()]
    return response.text


def is_valid_endpoint(app_id: int) -> bool:
    """check if valid endpoint"""
    response = requests.get(PRICE_FORMAT.format(app_id=app_id))
    return response.json().get(str(app_id)).get('success')

# def get_wishlist_by_id(steamid: int) -> list[dict]:
#     response = requests.get(WISHLIST_URL_FORMAT.format(
#         api_key=environ['API_KEY'], steamid=steamid))
#     print(response.json())


def get_endpoints() -> list[int]:
    pages = []
    app_id = 10
    while MAX_RESULTS > 0:
        if is_valid_endpoint(app_id):
            pages.append(app_id)
            MAX_RESULTS -= 1
        else:
            app_id += 10

    print("no more results")
    print(f"last app id = {app_id}")
    print(f"pages = {pages}")

    return pages


def get_price_info(app_ids_matrix: list[list[int]]) -> list[dict]:
    with multiprocessing.Pool(NUM_PROCESSES_PRICE) as pool:
        output = pool.map(get_from_db, app_ids_matrix)

    return output


if __name__ == "__main__":
    start_time = time.time()

    app_ids = get_endpoints()
    app_ids_matrix = np.array_split(app_ids, 2500)
    app_ids_matrix = [app_ids[x:x+25] for x in range(0, len(app_ids), 25)]

    print(get_price_info(app_ids_matrix))
    # save to steam_products.json

    end_time = time.time()
    print(f"Time taken: {end_time - start_time}")
    # print(get_from_steam_db([10, 20, 30]))
