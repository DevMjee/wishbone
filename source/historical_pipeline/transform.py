"""Script for transforming data for storage in S3"""

from pandas import DataFrame
import pandas as pd
import shutil
import os
import logging

FILEPATH = 'data/'
FACT_TABLE = 'Price_Record.csv'
LISTING_TABLE = 'DIM_Listing.csv'
GAME_TABLE = 'DIM_Game.csv'
PLATFORM_TABLE = 'DIM_Platform.csv'
# Do we store tracking in an RDS instead for short term with ids to games they want to track? (many to many)
TRACKING_TABLE = 'DIM_Tracking.csv'

PARQUET_HEAD = f'{FILEPATH}c20-wishbone-games/'
PARQUET_IN = f'{PARQUET_HEAD}input/'
PARQUET_OUT = f'{PARQUET_HEAD}output/'


def setup_directory() -> None:
    """Reset file structure for parquet files every run"""
    if os.path.exists(PARQUET_HEAD):
        shutil.rmtree(PARQUET_HEAD)
        logger.info('Parquet files reset')

    os.mkdir(PARQUET_HEAD)
    os.mkdir(PARQUET_IN)
    os.mkdir(PARQUET_OUT)
    os.mkdir(f'{PARQUET_IN}truck/')
    os.mkdir(f'{PARQUET_IN}payment_method/')
    os.mkdir(f'{PARQUET_IN}transaction/')


def merge_tables(fdf: DataFrame, pdf: DataFrame, tdf: DataFrame) -> None:
    """Function to merge files in one destination file"""
    try:
        merged = fdf.merge(pdf, on=PAYMENT_FKEY)
        merged = merged.merge(tdf, on=TRUCK_FKEY)

        # clean csv
        merged = clean(merged)

        # save merged dataframe to csv
        merged.to_csv(f'{FILEPATH}{DEST}', index=False)
        logger.info(f'{DEST} save to {FILEPATH}')

        # export DIM as parquet files
        export_dim(merged, tdf, 'truck')
        export_dim(merged, pdf, 'payment_method')
        export_fact(fdf, 'transaction')

    except ValueError:
        logger.error(f'Error while merging files to csv.')


def clean(df: DataFrame) -> DataFrame:
    """Function to remove rows with missing values in total column and drop fkey columns"""
    df = df.dropna(subset='total')
    # convert 1 and 0 to bool
    df['has_card_reader'] = df['has_card_reader'].astype(bool)
    return df


def export_dim(df: DataFrame, dim_df: DataFrame, filename: str) -> None:
    """Function to export dimension tables (not the fact table) as parquet files"""
    columns = [col for col in dim_df]
    df[columns].to_parquet(
        f'{PARQUET_IN}{filename}/{filename}.parquet', engine="pyarrow")


def export_fact(df: DataFrame, filename: str) -> None:
    """Function to export fact table as partitioned parquet files"""
    df['at'] = pd.to_datetime(df['at'])
    df['year'] = df['at'].dt.year
    df['month'] = df['at'].dt.month
    df['day'] = df['at'].dt.day
    df['hour'] = df['at'].dt.hour

    df.to_parquet(
        f'{PARQUET_IN}{filename}',
        engine="pyarrow",
        partition_cols=["year", "month", "day", "hour"],
        compression="zstd",
    )


if __name__ == "__main__":
    try:
        logger = logging.getLogger('extract')
        logging.basicConfig(filename=LOGFILE,
                            format='%(asctime)s: %(levelname)s: %(message)s',
                            level=logging.INFO)
    except:
        raise ValueError('Did you remember to run extract first?')

    setup_directory()

    # extract data from csv to df
    fact_df = pd.read_csv(f'{FILEPATH}{FACT_TABLE}')
    payment_df = pd.read_csv(f'{FILEPATH}{PAYMENT_TABLE}')
    truck_df = pd.read_csv(f'{FILEPATH}{TRUCK_TABLE}')
    merge_tables(fact_df, payment_df, truck_df)
