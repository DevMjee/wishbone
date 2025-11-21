"""Lambda function checking for extracting the latest discounts from the S3"""
from os import environ
from psycopg2.extensions import connection
from psycopg2 import connect
from dotenv import load_dotenv
import pandas as pd
import awswrangler
import boto3
from html_email import create_html_email

load_dotenv()


def get_games_price_dropped() -> pd.DataFrame:
    """gets the ids and name of the games that have dropped in price"""
    athena_query = """WITH price_cte AS (
            SELECT game_id, recording_date, price, 
            LAG(price) OVER (PARTITION BY game_id ORDER BY recording_date) as prev_price
            FROM listing
            )
            SELECT DISTINCT g.game_id, g.game_name, price_cte.price as new_price, price_cte.prev_price as old_price
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
    return connect(
        host=environ['RDS_HOST'],
        port=environ['PORT'],
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
    """returns a list of dictionaries of each game and the associated emails"""

    game_email_list = []

    for _, row in game_id_df.iterrows():
        game_id = row["game_id"]
        game_name = row["game_name"]
        new_price = row["new_price"]
        old_price = row["old_price"]

        emails_df = get_emails_for_dropped_price(game_id)

        list_emails = emails_df['email'].tolist()

        game_email_list.append(
            {"game_id": game_id, "game_name": game_name, "new_price": new_price, "old_price": old_price, "emails": list_emails})

    return game_email_list


def format_pennies_to_pounds(pennies: int) -> str:
    """takes the price in pennies and returns in pounds with £ symbol"""

    pounds = pennies / 100

    return f"£{pounds:.2f}"


def send_out_email(email_address, email_body, game_name):
    """sends the HTML email using boto3 to alert on drop of price"""
    SENDER_EMAIL = environ["SENDER_EMAIL"]
    CHARSET = "UTF-8"
    ses_client = boto3.client("ses", region_name="eu-west-2")

    ses_client.send_email(
        Source=SENDER_EMAIL,
        Destination={"ToAddresses": [email_address]},
        Message={
            "Body": {
                "Html": {
                    "Charset": CHARSET,
                    "Data": email_body,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": f"{game_name} is on sale!",
            },
        },
    )


def lambda_handler(event, context):
    """performs an athena query, a rds query and then sends emails if necessary """
    games_df = get_games_price_dropped()

    if games_df.empty:
        return {"message": "No games dropped in price"}

    price_dropped_emails = get_all_emails_with_game(games_df)

    print(price_dropped_emails)

    total_sent = 0

    for entry in price_dropped_emails:
        game_name = entry["game_name"]
        emails = entry["emails"]
        new_price = format_pennies_to_pounds(entry["new_price"])
        old_price = format_pennies_to_pounds(entry["old_price"])
        email_body = create_html_email(
            game_name, old_price, new_price)
        if emails is None:
            continue

        for email in emails:

            send_out_email(email, email_body, game_name)

            total_sent += 1

    return {"message": f"Sent {total_sent} emails"}


if __name__ == "__main__":
    print(lambda_handler({}, None))
