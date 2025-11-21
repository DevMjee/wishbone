from os import environ
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv
import boto3
import awswrangler as wr

load_dotenv()

session = boto3.Session(
    aws_access_key_id=environ["ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"],
    region_name="eu-west-2")
S3_BUCKET_NAME = environ["BUCKET_NAME"]


def get_connection():
    "returns connection to RDS"

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


def read_query_with_lambda():
    "test query on the S3 to ensure lambda has the correct permissions"
    query = wr.athena.read_sql_query(
        "select * from platform", database="wishbone-glue-db")
    return query


def lambda_handler(event, handler):
    "lambda handler function for the email service"
    db_conn = get_connection()
    s3_data = read_query_with_lambda()
    rds_data = get_data(db_conn)

    body = {"s3 data": f"{s3_data}", "rds data": f"{rds_data}"}

    return body


if __name__ == "__main__":
    print(lambda_handler({}, {}))
