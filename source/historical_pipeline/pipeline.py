"""Python module to access the RDS and download all price data for the day."""
import os
from os import environ
import shutil
from dotenv import load_dotenv
import logging
import pandas as pd
import pymysql.cursors

FILEPATH = 'data/'
LOGFILE = f'{FILEPATH}pipeline.log'
TABLE_NAMES = ('FACT_Price_Record', 'DIM_Game',
               'DIM_Listing', 'DIM_Platform')


def setup_directory() -> None:
    """Reset file structure for data run"""
    if os.path.exists(FILEPATH):
        shutil.rmtree(FILEPATH)

    os.mkdir(FILEPATH)


def extract_file_to_csv(name: str) -> None:
    """Function to extract data from rds"""
    try:
        with conn.cursor() as cursor:
            # extract table
            sql_query = """
            SELECT 
                * 
            FROM 
                `{0}`
            """.format(name)
            cursor.execute(sql_query)
            result = cursor.fetchall()

        # convert to dataframe
        df = pd.DataFrame(result)

        # save dataframe to csv
        df.to_csv(f'{FILEPATH}{name}.csv', index=False)
        logger.info(f'{name}.csv save to {FILEPATH}')

    except pymysql.err.ProgrammingError as e:
        logger.error(f'Error while trying to extract {name}')


if __name__ == "__main__":
    setup_directory()

    logger = logging.getLogger('extract')
    logging.basicConfig(filename=LOGFILE,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        level=logging.INFO)

    load_dotenv()

    # Connect to the database
    conn = pymysql.connect(host=environ['DB_HOST'],
                           user=environ['DB_USER'],
                           password=environ['DB_PASSWORD'],
                           database=environ['DB_NAME'],
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    # extract and save data
    for table in TABLE_NAMES:
        extract_file_to_csv(table)
