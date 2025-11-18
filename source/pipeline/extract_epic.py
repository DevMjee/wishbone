"""Script which scrapes data from Epic Games DB"""
from epicstore_api import EpicGamesStoreAPI
import pprint


api = EpicGamesStoreAPI()


def get_all_epic_games():
    api = EpicGamesStoreAPI(locale="en-GB", country="GB")

    all_games = []
    start = 0
    batch_size = 1000

    print("Fetching games from Epic Games Store")

    while True:
        try:
            response = api.fetch_catalog(
                count=batch_size,
                product_type="games/edition/base|bundles/games|editors|software/edition/base",
                namespace="",
                sort_by="title",
                sort_dir="ASC",
                start=start
            )

            elements = response.get("data", {}).get("Catalog", {}).get(
                "searchStore", {}).get("elements", [])
        except Exception as e:
            print(f"Error fetching batch at start={start}: {e}")
            break

        if not elements:
            break

        print(
            f"Fetched {len(elements)} games (total so far: {len(all_games) + len(elements)})")

        for game in elements:
            price_info = game.get("price", {}).get("totalPrice", {})

            game_data = {
                "id": game.get("id"),
                "title": game.get("title"),
                "namespace": game.get("namespace"),
                "slug": game.get("productSlug") or game.get("urlSlug"),
                "retailPrice": price_info.get("originalPrice", 0),
                "discountPrice": price_info.get("discountPrice", 0),
                "currencyCode": price_info.get("currencyCode", "GBP"),
                "discount": price_info.get("discount", 0),
                "onSale": price_info.get("discountPrice", 0) < price_info.get("originalPrice", 0)
            }

            all_games.append(game_data)

        start += batch_size

        if len(elements) < batch_size:
            break

    return all_games


if __name__ == "__main__":
    print("=" * 60)
    print("Extracting ALL Epic Games")
    print("=" * 60)

    games = get_all_epic_games()

    print(f"\n Total games fetched: {len(games)}\n")

    free_games = [g for g in games if g["retailPrice"] == 0]
    on_sale = [g for g in games if g["onSale"]]

    print(f"Free games: {len(free_games)}")
    print(f"Games on sale: {len(on_sale)}")

    print("\n" + "=" * 60)
    print("Sample games (first 10):")
    print("=" * 60)

    pprint.pprint(games[:10], width=100)
