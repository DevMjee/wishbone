import asyncio
import aiohttp
import json
import requests
from bs4 import BeautifulSoup

BASE_DIR = "https://www.gogdb.org/data/products"
HEADERS = {"User-Agent": "Mozilla/5.0"}

CONCURRENCY = 100


async def fetch_json(session, url):
    """Fetch JSON; return None if failed."""
    try:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.json()
    except:
        return None
    return None


async def extract_product(session, product_id: int):
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

    base_price = None
    final_price = None

    if prices_data:
        history = (
            prices_data
            .get("US", {})
            .get("USD", [])
        )

        if history:
            history.sort(key=lambda x: x.get("date", ""), reverse=True)
            latest = history[0]
            base_price = latest.get("price_base")
            final_price = latest.get("price_final")

    return {
        "product_id": product_id,
        "name": name,
        "base_price": base_price,
        "final_price": final_price
    }


async def extract_batch(product_ids):
    """Async extract for a batch of product IDs."""
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    timeout = aiohttp.ClientTimeout(total=600)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=HEADERS
    ) as session:

        tasks = [extract_product(session, pid) for pid in product_ids]
        results = []

        for task in asyncio.as_completed(tasks):
            item = await task
            if item:
                results.append(item)

        return results


def get_all_product_ids():
    """Scrape folder listing to get ALL product IDs."""
    r = requests.get(BASE_DIR + "/", headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    ids = []
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if href.endswith("/") and href[:-1].isdigit():
            ids.append(int(href[:-1]))

    ids.sort()
    return ids


if __name__ == "__main__":
    print("Fetching all product IDs...")
    product_ids = get_all_product_ids()
    print(f"Found {len(product_ids)} products")

    results = asyncio.run(extract_batch(product_ids))

    print(f"Extracted {len(results)} products")

    with open("products.json", "w") as f:
        json.dump(results, f, indent=4)

    print("Saved results to products.json")
