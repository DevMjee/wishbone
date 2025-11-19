"""Script for loading data to RDS"""
import json
import os
import psycopg2
from dotenv import load_dotenv
from datetime import date

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATA_PATH = "data/cleaned_data.json"


def get_connection():
    """Create and return new DB connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )


def get_or_create_game(cur, game_name: str, retail_price: int) -> int:
    """Return game_id: insert if game does not exist."""
    cur.execute(
        """
            SELECT game_id FROM wishbone.game WHERE game_name = %s;
        """,
        (game_name,)
    )
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute(
        """
            INSERT INTO wishbone.game (game_name, retail_price)
            VALUES (%s, %s)
            RETURNING game_id;
        """,
        (game_name, retail_price)
    )
    return cur.fetchone()[0]


def get_or_create_platform(cur, platform_name: str) -> int:
    """Return platform_id: insert if platform does not exist."""
    cur.execute(
        """
            SELECT platform_id FROM wishbone.platform WHERE platform_name = %s;
        """,
        (platform_name,)
    )
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute(
        """
            INSERT INTO wishbone.platform (platform_name)
            VALUES (%s)
            RETURNING platform_id;
        """,
        (platform_name,)
    )
    return cur.fetchone()[0]


def insert_listing(cur, game_id: int, platform_id: int, price: int, discount_percent: int, listing_date: date) -> None:
    """Insert a listing row"""
    cur.execute(
        """
            INSERT INTO wishbone.listing (game_id, platform_id, price, discount_percent, recording_date)
            VALUES (%s, %s, %s, %s, %s);
        """,
        (game_id, platform_id, price, discount_percent, listing_date)
    )


def load_data() -> None:
    """Main load function"""
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    conn = get_connection()
    cur = conn.cursor()

    try:
        for product in data:
            game_name = product["game_name"]
            retail_price = product["retail_price"]
            platform_name = product["platform_name"]
            listing_date = product["listing_date"]
            discount_percent = product["discount_percent"]
            price = product["price"]

            game_id = get_or_create_game(cur, game_name, retail_price)
            platform_id = get_or_create_platform(cur, platform_name)

            insert_listing(cur, game_id, platform_id, price,
                           discount_percent, listing_date)

            conn.commit()
            print("Load completed successfully")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_data()
