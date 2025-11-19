"Module to test that the modules used in the ETL script work with Lambda Functions"

from os import environ
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup


URL = "https://store.steampowered.com/api/appdetails/?appids={appid}&cc=uk&filters=price_overview"
BASE_DIR = "https://www.gogdb.org/data/products"
HEADERS = {"User-Agent": "Mozilla/5.0"}

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
    r = requests.get(BASE_DIR + "/", headers=HEADERS)
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


def lambda_handler(event, context):
    "lambda handler function to check there is data in the database"
    db_conn = get_connection()
    db_data = get_data(db_conn)
    steam_response = get_from_steam_db(10)
    ids = get_all_product_ids()

    data = {"body": f"{[db_data], [ids]}", "statusCode": f"{steam_response}"}

    return data


if __name__ == "__main__":

    print(lambda_handler({}, {}))
