"""Lambda function for deleting user personal data upon request"""

from os import environ
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    "function to return connection to the RDS database"
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


def lambda_handler(event, context):
    db_conn = get_connection()
    data = get_data(db_conn)
    return {"data": f"{data}"}


if __name__ == "__main__":

    print(lambda_handler({}, {}))
