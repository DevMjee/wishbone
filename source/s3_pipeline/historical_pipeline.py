import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import awswrangler as wr
import pandas as pd
from sqlalchemy import create_engine, text

load_dotenv()

BUCKET = "c20-wishbone-s3"
BASE_S3_PATH = f"s3://{BUCKET}/input"
VALID_TABLES = {"game", "platform", "listing"}

S3_GAME = f"{BASE_S3_PATH}/game/game.parquet"
S3_PLATFORM = f"{BASE_S3_PATH}/platform/platform.parquet"
S3_LISTING_BASE = f"{BASE_S3_PATH}/listing/"

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

CONNECTION_STRING = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_engine():
    """Create DB engine"""
    return create_engine(CONNECTION_STRING)


def extract_table(table: str) -> pd.DataFrame:
    """Extract full table data from RDS into a pandas df"""
    if table not in VALID_TABLES:
        raise ValueError(f"Invalid table name: {table}")

    query = text(f"SELECT * FROM wishbone.{table};")

    engine = get_engine()
    df = pd.read_sql(query, engine)

    print(f"Extracted data from {table}: {len(df)} rows")
    return df


def transform_listing(df: pd.DataFrame) -> pd.DataFrame:
    """Safety check to ensure recording_date is date"""
    df["recording_date"] = pd.to_datetime(df["recording_date"]).dt.date
    return df


def load_dim_table(df: pd.DataFrame, s3_path: str):
    """Append to parquet file for game & platform, create file if doesn't exist"""
    exists = wr.s3.does_object_exist(s3_path)

    wr.s3.to_parquet(
        df=df,
        path=s3_path,
        index=False,
        dataset=True,
        mode="append" if exists else "overwrite"
    )

    action = "appended to" if exists else "created"
    print(f"Dimension {action}: {s3_path}")


def load_listing_partitioned(df: pd.DataFrame):
    """Write parquet files by year/month/day"""
    df["recording_date"] = pd.to_datetime(df["recording_date"])
    df["year"] = df["recording_date"].dt.year
    df["month"] = df["recording_date"].dt.month
    df["day"] = df["recording_date"].dt.day

    wr.s3.to_parquet(
        df=df,
        path=S3_LISTING_BASE,
        index=False,
        dataset=True,
        partition_cols=["year", "month", "day"]
    )

    print(f"Load and partitioning listing to s3")


def delete_old_listing_data():
    """Delete all listing rows that are not from today's date"""
    today = datetime.now(timezone.utc).date()

    query = text("""
            DELETE FROM wishbone.listing
            WHERE recording_date::date <> :today;        
    """)

    engine = get_engine()

    with engine.begin() as conn:
        result = conn.execute(query, {"today": today})
        deleted = result.rowcount

    print(f"Cleanup, deleted {deleted} outdated listing rows from RDS")


def main():
    """Main Historical Pipeline"""
    print("Starting Historical Pipeline")

    games_df = extract_table("game")
    platforms_df = extract_table("platform")
    listings_df = extract_table("listing")

    listings_df = transform_listing(listings_df)

    load_dim_table(games_df, S3_GAME)
    load_dim_table(platforms_df, S3_PLATFORM)
    load_listing_partitioned(listings_df)

    delete_old_listing_data()

    print("Historical pipeline complete")


def lambda_handler(event, context):
    main()
    return {"status": "success", "msg": "Historical pipeline completed"}
