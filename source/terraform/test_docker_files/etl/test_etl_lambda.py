"Module to test that the modules used in the ETL script work with Lambda Functions"

from os import environ
import asyncio
import aiohttp
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from forex_python.converter import CurrencyRates

URL = "https://store.steampowered.com/api/appdetails/?appids={appid}&cc=uk&filters=price_overview"
BASE_DIR = "https://www.gogdb.org/data/products"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CONCURRENCY = 100
TIMEOUT = 600

load_dotenv()


def get_from_steam_db(appid: int) -> dict:
    """Pull games, ids, and prices from database"""
    response = requests.get(URL.format(appid=appid), timeout=10)

    return response


def get_connection():
    "function to return connection to the RDS database"
    conn = connect(
        host=environ["RDS_HOST"],
        user=environ["RDS_USERNAME"],
        password=environ["RDS_PASSWORD"],
        dbname=environ["DB_NAME"],
        port=environ["PORT"],
        cursor_factory=RealDictCursor
    )

    return conn


def get_data(conn: connection):
    "connects to database, connects to wishbone schema and checks data is there"
    cursor = conn.cursor()
    cursor.execute("""set search_path to wishbone;
                   select * from platform;""")
    data = cursor.fetchall()
    cursor.close()
    return data


def get_all_product_ids():
    """Scrape folder listing to get ALL product IDs."""
    r = requests.get(BASE_DIR + "/", headers=HEADERS, timeout=600)
    soup = BeautifulSoup(r.text, "html.parser")
    ids = []
    count = 0
    for link in soup.find_all("a"):
        count += 1
        href = link.get("href", "")
        if href.endswith("/") and href[:-1].isdigit():
            ids.append(int(href[:-1]))

    ids.sort()
    return ids


async def fetch_json(session, url):
    """Fetch JSON: return None if failed."""
    try:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.json()
    except:
        return None
    return None


async def extract_product(session, product_id: int, usd_to_gbp: float):
    """Extract product.json + prices.json from a single product folder."""
    product_url = f"{BASE_DIR}/{product_id}/product.json"
    prices_url = f"{BASE_DIR}/{product_id}/prices.json"

    product_data, prices_data = await asyncio.gather(
        fetch_json(session, product_url),
        fetch_json(session, prices_url)
    )

    if not product_data:
        return None

    name = product_data.get("title")
    if not name:
        return None

    base_price_cents = None
    final_price_cents = None
    base_price_gbp_pence = None
    final_price_gbp_pence = None

    if prices_data:
        history = (
            prices_data
            .get("US", {})
            .get("USD", [])
        )

        if history:
            history.sort(key=lambda x: x.get("date", ""), reverse=True)
            latest = history[0]
            base_price_cents = latest.get("price_base")
            final_price_cents = latest.get("price_final")

            if base_price_cents is not None:
                base_usd = base_price_cents / 100
                base_gbp = base_usd * usd_to_gbp
                base_price_gbp_pence = int(round(base_gbp * 100))

            if final_price_cents is not None:
                final_usd = final_price_cents / 100
                final_gbp = final_usd * usd_to_gbp
                final_price_gbp_pence = int(round(final_gbp * 100))

    return {
        "product_id": product_id,
        "name": name,
        "base_price_gbp_pence": base_price_gbp_pence,
        "final_price_gbp_pence": final_price_gbp_pence
    }


async def extract_batch(product_ids, usd_to_gbp: float):
    """Async extract for a batch of product IDs."""
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=HEADERS
    ) as session:

        tasks = [extract_product(session, pid, usd_to_gbp)
                 for pid in product_ids]
        results = []

        for task in asyncio.as_completed(tasks):
            item = await task
            if item:
                results.append(item)

        return results


def extract_gog():
    print("Fetching all product IDs...")
    product_ids = get_all_product_ids()
    print(f"Found {len(product_ids)} products")

    print("Fetching USD -> GBP conversion rate")
    c = CurrencyRates()
    usd_to_gbp_rate = c.get_rate("USD", "GBP")
    print(f"Current USD -> GBP rate: {usd_to_gbp_rate}")

    results = asyncio.run(extract_batch(product_ids, usd_to_gbp_rate))
    return results


def lambda_handler(event, context):
    "lambda handler function to check there is data in the database"
    db_conn = get_connection()
    db_data = get_data(db_conn)
    steam_response = get_from_steam_db(10)
    ids = get_all_product_ids()
    gog_result = extract_gog()

    data = {"body": f"{[db_data], [ids[-1]], [gog_result[-1]]}",
            "statusCode": f"{steam_response}"}

    return data


if __name__ == "__main__":

    print(lambda_handler({}, {}))
