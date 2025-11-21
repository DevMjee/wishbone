"Module for testing the email service lambda"

from os import environ
import awswrangler as wr
import boto3
from dotenv import load_dotenv

load_dotenv()
session = boto3.Session(
    aws_access_key_id=environ["ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"],
    region_name="eu-west-2")
S3_BUCKET_NAME = environ["BUCKET_NAME"]


def read_query_with_lambda():
    "test query on the S3 to ensure lambda has the correct permissions"
    query = wr.athena.read_sql_query(
        "select * from platform", database="wishbone-glue-db")
    return query


def lambda_handler(event, handler):
    "lambda handler function for the email service"
    data = read_query_with_lambda()

    body = {"data": f"{data}"}

    return body


if __name__ == "__main__":
    print(lambda_handler({}, {}))
