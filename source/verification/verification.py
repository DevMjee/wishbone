"""Lambda function checking emails on RDS are verified"""
from os import environ
from psycopg2.extensions import connection
from psycopg2 import connect
from dotenv import load_dotenv
import pandas as pd
import boto3

load_dotenv()


def get_db_connection() -> connection:
    """Returns a live connection from the database."""
    return connect(
        host=environ['RDS_HOST'],
        port=environ['PORT'],
        user=environ['RDS_USERNAME'],
        password=environ['RDS_PASSWORD'],
        dbname=environ['DB_NAME']
    )


def get_emails_in_tracking_table() -> list:
    """gets the emails of the people tracking games"""
    conn = get_db_connection()
    query = """SELECT DISTINCT email
                    FROM wishbone.tracking
                    """
    emails_df = pd.read_sql(query, con=conn)

    list_emails = emails_df['email'].tolist()

    return list_emails


def verify_email(user_email: str, ses_client: boto3.client) -> bool:
    """checks if the email is verified or not"""

    response = ses_client.list_verified_email_addresses()
    verified_emails = response.get("VerifiedEmailAddresses")

    if user_email in verified_emails:
        return True
    return False


def remove_unverified_email(unverified_email: str):
    """gets the emails of the people tracking games"""
    conn = get_db_connection()
    cur = conn.cursor()
    query = """DELETE
                    FROM wishbone.tracking
                WHERE email = %s
                    """
    cur.execute(query, (unverified_email,))
    conn.commit()
    cur.close()
    conn.close()


def lambda_handler(event, context):
    """takes the emails from the RDS and drops any that have not been verified"""

    tracking_emails = get_emails_in_tracking_table()
    ses = boto3.client('ses')
    for email in tracking_emails:
        if verify_email(email, ses) is False:
            remove_unverified_email(email)
