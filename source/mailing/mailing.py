"""Lambda function checking for extracting the latest discounts from the S3"""
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.extensions import connection
from psycopg2 import connect
from dotenv import dotenv_values
from os import environ
import pandas as pd
import awswrangler


ATHENA_QUERY = """WITH price_cte AS (
            SELECT game_id, recording_date, price, 
            LAG(price) OVER (PARTITION BY game_id ORDER BY date) as prev_price
            FROM listing
            )
            SELECT DISTINCT game_id, game_name 
                FROM price_cte 
            JOIN game g on 
                price_cte.game_id = g.game_id
            WHERE price < prev_price"""


def get_games_id_price_dropped(sql_query: str) -> pd.DataFrame:
    """gets the ids of the games that have dropped in price"""
    game_id_df = awswrangler.athena.read_sql_query(
        sql_query, database="XXXXXXX")

    return game_id_df


def get_db_connection() -> connection:
    """Returns a live connection from the database."""
    config = dotenv_values()
    return connect(
        host=environ('RDS_ENDPOINT'),
        port=5432,
        user=environ('RDS_USERNAME'),
        password=environ('RDS_PASSWORD'),
        dbname=environ('DB_NAME'),
        cursor_factory=RealDictCursor
    )


def get_emails_for_dropped_price(id: int) -> pd.DataFrame:
    """gets the emails of the people tracking games"""
    query = f"""SELECT email 
                        FROM wishbone.tracking
                    WHERE game_id = {id}
                    """
    emails_df = pd.read_sql(query, con=connection)


def lambda_handler(event, context):
    return {'event': event, 'context': context}


if __name__ == "__main__":
    pass
