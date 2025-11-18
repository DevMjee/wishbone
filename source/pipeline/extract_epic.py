"""Script which scrapes data from Epic Games DB"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from epicstore_api import EpicGamesStoreAPI
import threading
import pprint

api = EpicGamesStoreAPI()
lock = threading.Lock()


def fetch_game(slug: str | None, namespace: str | None) -> dict:
    """Fetch a single game and return data"""
    try:
        product = api.get_product(slug)

    except Exception:
        return {
            "id": slug,
            "title": slug,
            "namespace": namespace,
            "slug": slug,
            "retailPrice": 0,
            "discountPrice": 0
        }

    try:
        title = product.get("title", slug)
        pages = product.get("pages", [])

        first_offer = None
        for page in pages:
            offer = page.get("offer")
            if offer and offer.get("id"):
                first_offer = (page["namespace"], offer["id"])
                break

        retail_price = 0
        discount_price = 0
        game_id = None
        namespace_final = product.get("namespace") or namespace

        if first_offer:
            offer_ns, offer_id = first_offer

            offer_data = api.get_offers_data(
                api.OfferData(offer_ns, offer_id))[0]
            catalog = offer_data["data"]["Catalog"]["catalogOffer"]

            game_id = catalog.get("id", game_id)
            namespace_final = catalog.get("namespace", namespace_final)

            total_price = (catalog.get("price", {}).get("totalPrice", {}))

            retail_price = total_price.get("originalPrice", 0)
            discount_price = total_price.get("discountPrice", 0)
        else:
            prod_price = product.get("price", {})
            total_price = prod_price.get("totalPrice") or {}

            retail_price = total_price.get("originalPrice") or 0
            discount_price = total_price.get("discountPrice") or 0

        return {
            "id": game_id,
            "title": title,
            "namespace": namespace_final,
            "slug": slug,
            "retailPrice": retail_price,
            "discountPrice": discount_price
        }

    except Exception as e:
        print(f"Error while processing {slug}: {e}")
        return None


def extract_all_games(max_workers=20) -> list[dict]:
    """Extract all games and their prices from Epic Games Store"""

    product_map = api.get_product_mapping()
    product_items = list(product_map.items())

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_game, slug, namespace): (slug, namespace)
            for slug, namespace in product_items
        }

        for future in as_completed(futures):
            data = future.result()
            if data:
                with lock:
                    results.append(data)

    return results


def extract_real_games():
    try:

        response = api.fetch_store_games(
            count=10000,
            product_type="games",
            allow_countries="GB",
            with_price=True,
            sort_by="title",
            sort_dir="ASC"
        )

        print(f"Response type: {type(response)}")
        print(
            f"Response keys (if dict): {response.keys() if isinstance(response, dict) else "Not a dict"}")
        print(
            f"First item preview: {response[0] if isinstance(response, list) and len(response) > 0 else response}")

        if isinstance(response, list):
            elements = response
        else:
            elements = response.get("data", response.get("elements", []))

        results = []
        for item in elements:

            if len(results) == 0:
                print(
                    f"First item structure: {item.keys() if isinstance(item, dict) else item}")

            total_price = item.get("price", {}).get("totalPrice", {})

            results.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "namespace": item.get("namespace"),
                "slug": item.get("productSlug"),
                "retailPrice": total_price.get("originalPrice", 0),
                "discountPrice": total_price.get("discountPrice", 0)
            })

        print(f"Results created: {len(results)}")
        return results

    except Exception as e:
        print(f"Error in extract_real_games: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    print("Extracting ALL Epic Games")

    all_games = extract_real_games()

    print(f"\n Extracted {len(all_games)} games\n")

    print("Example preview (first 50): ")
    pprint.pprint(all_games[:5])
