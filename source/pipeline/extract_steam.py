"""Script which gets data from steam web api"""
from os import environ
import requests
import multiprocessing
import time
import json
import numpy as np
import pandas as pd

URL_FORMAT = "https://store.steampowered.com/api/appdetails/?appids={appid}&cc=uk"
# WISHLIST_URL_FORMAT = "https://api.steampowered.com/IWishlistService/GetWishlist/v1/?access_token={api_key}&steamid={steamid}"
MAX_RESULTS = 10000
NUM_PROCESSES_INFO = 16
NUM_PROCESSES_PRICE = 64


def get_from_steam_db(app_ids: list[int]) -> dict:
    """Pull games, ids, and prices from api"""
    app_ids = [str(app_id) for app_id in app_ids]
    app_ids_csv = ','.join(app_ids)
    # print(app_ids_csv)
    response = requests.get(PRICE_URL_FORMAT.format(app_ids=app_ids_csv))
    # response_list = [{k: v} for k, v in response.json().items()]
    return response.text


def is_valid_steam_endpoint(appid: int) -> bool:
    """Pull games, ids, and prices from database"""
    response = requests.get(URL_FORMAT.format(appid=appid))
    return response.json().get(str(appid)).get('success')

# def get_wishlist_by_id(steamid: int) -> list[dict]:
#     response = requests.get(WISHLIST_URL_FORMAT.format(
#         api_key=environ['API_KEY'], steamid=steamid))
#     print(response.json())


def check_new_endpoints() -> int:
    app_id = 10
    failures = 100
    while failures > 0:
        try:
            if is_valid_steam_endpoint(app_id):
                failures -= 1
            app_id += 10
        except:
            continue


def check_new_endpoints() -> list[int]:
    is_more_results = True
    page_index = 0
    pages = [0]
    while is_more_results:
        response = requests.get(GAME_INFO_URL_FORMAT.format(
            api_key=environ['API_KEY'], max_results=MAX_RESULTS, page_index=page_index))
        output = response.json()
        is_more_results = output.get('response').get('have_more_results')

        if is_more_results:
            last_appid = output.get('response').get('last_appid')
            page_index = last_appid
            pages.append(last_appid)

    print("no more results")
    print(f"last app id = {app_id}")
    print(f"pages = {pages}")

    return app_id
    return pages


def fetch_game_info_page(page_index: int) -> list[dict]:
    response = requests.get(
        GAME_INFO_URL_FORMAT.format(api_key=environ['API_KEY'], max_results=MAX_RESULTS, page_index=page_index))

    return response.json().get('response').get('apps')


def get_game_info() -> list[dict]:
    pages = check_new_endpoints()
    with multiprocessing.Pool(NUM_PROCESSES_INFO) as pool:
        output = pool.map(fetch_game_info_page, pages)

    # output = fetch_game_info_page(0)
    output = list(np.concatenate(output))
    return output


def get_price_info(app_ids_matrix: list[list[int]]) -> list[dict]:
    with multiprocessing.Pool(NUM_PROCESSES_PRICE) as pool:
        output = pool.map(get_from_steam_db, app_ids_matrix)

    return output


if __name__ == "__main__":
    start_time = time.time()
    load_dotenv()
    output = get_game_info()
    df = pd.DataFrame(output)
    with open("data/a_file.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4)

    print(df)
    app_ids = list(df['appid'])
    app_ids_matrix = np.array_split(app_ids, 2500)
    app_ids_matrix = [app_ids[x:x+25] for x in range(0, len(app_ids), 25)]

    print(get_price_info(app_ids_matrix))

    end_time = time.time()
    print(f"Time taken: {end_time - start_time}")
    # print(get_from_steam_db([10, 20, 30]))
