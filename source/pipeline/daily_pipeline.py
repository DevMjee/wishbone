"""Lambda function checking emails on RDS are verified"""
from os import environ
import awswrangler
import boto3
from dotenv import load_dotenv
import pandas as pd
import multiprocessing
import time

from extract import extract_games
from transform import transform_all
from load import load_data

NUM_PROCESSES = 64
# Most recent duration test
#     16: 242 seconds
#     32: 130 seconds
# --> 64: 118 seconds
#     128: 491 seconds


load_dotenv()


def get_game_names() -> list[str]:
    """get all names of games we're tracking"""
    athena_query = """
    SELECT
        DISTINCT g.game_name,
        l.recording_date
    FROM 
        game g
    JOIN
        listing l
    ON
        g.game_id = l.game_id
    ORDER BY
        l.recording_date
    DESC
    LIMIT
        100
    ;
    """
    # query above loads latest hundred unique game names

    session = boto3.Session(aws_access_key_id=environ["ACCESS_KEY_ID"],
                            aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"], region_name='eu-west-2')

    game_names = pd.DataFrame(awswrangler.athena.read_sql_query(
        athena_query, database="wishbone-glue-db", boto3_session=session))

    results = game_names['game_name'].to_list()

    if len(results) == len(set(results)):
        return results

    raise ValueError(
        'Not unique names! How could this happen? The SQL Query was magnificent!')


def pipeline(game_inputs: list[str]) -> None:
    """pipeline for multiprocessing"""
    extract_games(game_inputs)
    transform_all()
    load_data()


def run_extract():
    """takes the game names from the S3 game table via athena and runs the pipeline on them"""
    games = get_game_names()
    size = int(len(games)/4)
    game_chunks = [games[i::size] for i in range(size)]

    with multiprocessing.Pool(NUM_PROCESSES) as pool:
        pool.map(pipeline, game_chunks)


if __name__ == "__main__":
    start_time = time.time()
    run_extract()
    end_time = time.time()
    print(f'Time taken: {end_time - start_time}')
