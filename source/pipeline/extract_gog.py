"""Extract script which gets data from GOG DB"""
import json
import os
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from forex_python.converter import CurrencyRates

BASE_DIR = "https://www.gogdb.org/data/products"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_PATH = 'data/gog_products.json'
CONCURRENCY = 100
TIMEOUT = 600


async def fetch_json(session: aiohttp.ClientSession, url: str):
    """Fetch JSON: return None if failed."""
    try:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.json()
            if r.status == 404:
                print(f"404: File not found for {url}")
                return None
            if r.status == 429:
                print(f"429: Rate limit hit for {url}")
                return None
            if r.status == 500:
                print(f"500: Server error for {url}")
                return None

            print(f"{r.status}: Error for {url}")
            return None

    except Exception as e:
        print(f"Exception error fetching {url}: {e}")
        return None


async def extract_product(session: aiohttp.ClientSession, product_id: int, usd_to_gbp: float) -> dict | None:
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


async def extract_batch(product_ids: list[int], usd_to_gbp: float) -> list[dict]:
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


def get_all_product_ids() -> list[int]:
    """Scrape folder listing to get ALL product IDs."""
    r = requests.get(BASE_DIR + "/", headers=HEADERS, timeout=TIMEOUT)
    soup = BeautifulSoup(r.text, "html.parser")

    ids = []
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if href.endswith("/") and href[:-1].isdigit():
            ids.append(int(href[:-1]))

    ids.sort()
    return ids


def extract_gog():
    """Extract all game data from GOG DB"""
    print("Fetching all product IDs...")
    product_ids = get_all_product_ids()
    print(f"Found {len(product_ids)} products")

    print("Fetching USD -> GBP conversion rate")
    c = CurrencyRates()
    usd_to_gbp_rate = c.get_rate("USD", "GBP")
    print(f"Current USD -> GBP rate: {usd_to_gbp_rate}")

    results = asyncio.run(extract_batch(product_ids, usd_to_gbp_rate))

    print(f"Extracted {len(results)} products")

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print("Saved results to products.json")


if __name__ == "__main__":
    extract_gog()
