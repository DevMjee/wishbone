"""Lambda function checking for extracting the latest discounts from the S3"""
from os import environ
from psycopg2.extensions import connection
from psycopg2 import connect
from dotenv import load_dotenv
import pandas as pd
import awswrangler
import boto3


def get_games_price_dropped() -> pd.DataFrame:
    """gets the ids and name of the games that have dropped in price"""
    load_dotenv()
    athena_query = """WITH price_cte AS (
            SELECT game_id, recording_date, price, 
            LAG(price) OVER (PARTITION BY game_id ORDER BY recording_date) as prev_price
            FROM listing_parquet
            )
            SELECT DISTINCT g.game_id, g.game_name 
                FROM price_cte 
            JOIN game g on 
                price_cte.game_id = g.game_id
            WHERE price < prev_price"""

    session = boto3.Session(aws_access_key_id=environ["ACCESS_KEY_ID"],
                            aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"], region_name='eu-west-2')

    game_id_df = awswrangler.athena.read_sql_query(
        athena_query, database="wishbone-glue-db", boto3_session=session)

    return game_id_df


def get_db_connection() -> connection:
    """Returns a live connection from the database."""
    load_dotenv()
    return connect(
        host=environ['RDS_HOST'],
        port=5432,
        user=environ['RDS_USERNAME'],
        password=environ['RDS_PASSWORD'],
        dbname=environ['DB_NAME']
    )


def get_emails_for_dropped_price(g_id: int) -> pd.DataFrame:
    """gets the emails of the people tracking games"""
    conn = get_db_connection()
    query = """SELECT email
                        FROM wishbone.tracking
                    WHERE game_id = %s
                    """
    emails_df = pd.read_sql(query, con=conn, params=(g_id,))

    return emails_df


def get_all_emails_with_game(game_id_df: pd.DataFrame) -> list[dict]:
    """returns a json style thing of games associated with each email"""

    game_email_list = []

    for _, row in game_id_df.iterrows():
        game_id = row["game_id"]
        game_name = row["game_name"]

        emails_df = get_emails_for_dropped_price(game_id)

        list_emails = emails_df['email'].tolist()

        game_email_list.append(
            {"game_id": game_id, "game_name": game_name, "emails": list_emails})

    return game_email_list


def lambda_handler(event, context):
    """performs an athena query, a rds query and then returns """
    games_df = get_games_price_dropped()

    if games_df.empty:
        return {"message": "no games dropped in price"}

    price_dropped_emails = get_all_emails_with_game(games_df)

    ses = boto3.client("ses")
