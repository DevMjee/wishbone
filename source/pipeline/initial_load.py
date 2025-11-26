"""Lambda function checking emails on RDS are verified"""
from os import environ
import awswrangler
import boto3
from dotenv import load_dotenv
import pandas as pd
from psycopg2.extensions import connection
from psycopg2 import connect

from extract import extract_games

load_dotenv()


def get_game_names() -> list[str]:
    """get all names of games we're tracking"""
    athena_query = """SELECT game_name FROM game"""

    session = boto3.Session(aws_access_key_id=environ["ACCESS_KEY_ID"],
                            aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"], region_name='eu-west-2')

    game_names = pd.DataFrame(awswrangler.athena.read_sql_query(
        athena_query, database="wishbone-glue-db", boto3_session=session))

    return game_names['game_name'].to_list()


def run_extract():
    """takes the game names from the S3 game table via athena and runs the pipeline on them"""
    games = get_game_names()
    for game in games:
        extract_games(game)


if __name__ == "__main__":
    run_extract()
