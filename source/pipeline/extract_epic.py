"""Script which scrapes all games from GOG database"""
import requests
from bs4 import BeautifulSoup

BASE_DIR = "https://www.gogdb.org/data/products"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_json(url: str):
    """Fetch a JSON file."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def get_all_product_ids() -> list:
    """Scrape the directory listing and extract all product ID folders."""
    r = requests.get(BASE_DIR + "/", headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    ids = []

    for link in soup.find_all("a"):
        href = link.get("href", "")
        if href.endswith("/") and href[:-1].isdigit():
            ids.append(int(href[:-1]))

    ids.sort()
    return ids


def extract_single_product(product_id: int) -> dict | None:
    """Extract product name + base and latest price."""
    product_url = f"{BASE_DIR}/{product_id}/product.json"
    prices_url = f"{BASE_DIR}/{product_id}/prices.json"

    product_data = fetch_json(product_url)
    if not product_data:
        return None

    name = product_data.get("title")
    if not name:
        return None

    prices_data = fetch_json(prices_url)
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
        "final_price": final_price,
    }


def extract_all_products() -> list:
    """Extract ALL GOG products by scraping product folder names."""
    product_ids = get_all_product_ids()
    print(f"Found {len(product_ids)} product folders.")

    results = []

    for pid in product_ids:
        print(f"Extracting product {pid}...")
        data = extract_single_product(pid)

        if data:
            results.append(data)

    return results


if __name__ == "__main__":
    products = extract_all_products()
    print(f"\nExtracted {len(products)} products total.")
