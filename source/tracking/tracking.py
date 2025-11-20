"""Lambda function for deleting user personal data upon request"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection


def get_connection() -> connection:
    conn = psycopg2.connect()


def subscribe_to_game(game_id: int, email: str, conn: connection) -> dict:
    insert_query = """
                    INSERT INTO tracking(
                        email, game_id)
                    VALUES
                        (%s, %s)
                    ON CONFLICT DO NOTHING
                    """

    cur = conn.cursor()

    cur.execute(insert_query, (email, game_id,))

    cur.close()


def remove_email(email: str, conn: connection) -> dict:
    delete_query = """
                    DELETE FROM tracking
                    WHERE email = %s
                    RETURNING tracking_id
                    """

    cur = conn.cursor()

    cur.execute(delete_query, (email,))

    deleted_id = cur.fetchall()

    conn.commit()

    cur.close()

    return {'status'}


def lambda_handler(event, context):
    conn = get_connection()
    if event.get('subscribe') is True:
        subscribe_to_game(event.get('game_id'), event.get('email'), conn)

    elif event.get('subscribe') is False:
        remove_email(event.get('email'), conn)

    return {'event': event, 'context': context}


if __name__ == "__main__":
    load_dotenv()
    lambda_handler(
        {'subscribe': False, 'email': 'test@test.com', 'game_id': 1})
