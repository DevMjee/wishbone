"""Lambda function for deleting user personal data upon request"""
from os import environ
from dotenv import load_dotenv
import boto3
import psycopg2
from psycopg2.extensions import connection


def get_connection() -> connection:
    """Connects to the RDS"""
    conn = psycopg2.connect(f"""
                            dbname={environ['DB_NAME']}
                            user={environ['RDS_USERNAME']}
                            password={environ['RDS_PASSWORD']}
                            host={environ['RDS_HOST']}
                            port={environ['PORT']}
                            """)
    return conn


def subscribe_to_game(game_id: int, email: str, conn: connection) -> dict:
    """Adds the email to the tracking table with the game ID"""
    insert_query = """
                    INSERT INTO wishbone."tracking"(
                        email, game_id)
                    VALUES
                        (%s, %s)
                    ON CONFLICT DO NOTHING;
                    """

    cur = conn.cursor()

    try:
        cur.execute(insert_query, (email, game_id,))
    except psycopg2.errors.ForeignKeyViolation:
        return {'status': 'error', 'msg': f'game with id {game_id} is not on record'}

    conn.commit()

    cur.close()

    return {'status': 'success', 'msg': f"email '{email}' is now tracking game with id '{game_id}'"}


def remove_email(email: str, conn: connection) -> dict:
    """Removes the users email from the tracking table"""
    delete_query = """
                    DELETE FROM wishbone."tracking"
                    WHERE email = %s;
                    """

    cur = conn.cursor()

    cur.execute(delete_query, (email,))

    if cur.rowcount == 0:
        return {'status': 'error', 'msg': f"email '{email}' does not exist on the database"}

    conn.commit()

    cur.close()

    return {'status': 'success', 'msg': f"removed email '{email}' from database"}


def verify_email(user_email: str) -> bool:
    """checks if the email is verified or not"""

    ses = boto3.client('ses')
    response = ses.list_verified_email_addresses()
    verified_emails = response.get("VerifiedEmailAddresses")

    if user_email in verified_emails:
        return True
    return False


def lambda_handler(event, context):
    conn = get_connection()
    if event.get('subscribe') == "True":
        email = event.get('email')
        if verify_email(email) is False:
            ses = boto3.client('ses')
            ses.verify_email_identity(EmailAddress=email,)

        return subscribe_to_game(event.get('game_id'), event.get('email'), conn)

    if event.get('subscribe') == "False":
        return remove_email(event.get('email'), conn)

    return {'status': 'error', 'msg': ''}


def populate_test_emails():
    for i in range(2, 5):
        print(lambda_handler(
            {'subscribe': 'True', 'email': f'test_{i}@testdomain{i}.com', 'game_id': i}, {}))


if __name__ == "__main__":
    load_dotenv()
    populate_test_emails()
