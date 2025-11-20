"""Lambda function for deleting user personal data upon request"""
from os import environ
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection


def get_connection() -> connection:
    conn = psycopg2.connect(f"""
                            dbname={environ['DB_NAME']}
                            user={environ['RDS_USERNAME']}
                            password={environ['RDS_PASSWORD']}
                            host={environ['RDS_HOST']}
                            port={environ['PORT']}
                            """)
    return conn


def subscribe_to_game(game_id: int, email: str, conn: connection) -> dict:
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

    cur.close()

    conn.commit()

    return {'status': 'success', 'msg': f"email '{email}' is now tracking game with id '{game_id}'"}


def remove_email(email: str, conn: connection) -> dict:
    delete_query = """
                    DELETE FROM wishbone."tracking"
                    WHERE email = %s
                    RETURNING tracking_id;
                    """

    cur = conn.cursor()

    cur.execute(delete_query, (email,))

    conn.commit()

    cur.close()

    return {'status': 'success', 'msg': f"removed email '{email}' from database"}


def lambda_handler(event, context):
    conn = get_connection()
    if event.get('subscribe') == "True":
        return subscribe_to_game(event.get('game_id'), event.get('email'), conn)

    elif event.get('subscribe') == "False":
        return remove_email(event.get('email'), conn)

    return {'status': 'error', 'msg': ''}


if __name__ == "__main__":
    load_dotenv()
    print(lambda_handler(
        {'subscribe': False, 'email': 'test@test.com', 'game_id': 2}, {}))
