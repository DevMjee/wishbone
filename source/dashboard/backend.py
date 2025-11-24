import aioboto3
import json
import asyncio
from psycopg2 import connect
from psycopg2.extensions import connection
import bcrypt
import pandas as pd


def check_login(username: str, password: bytes, conn: connection) -> bool:
    check_query = f"""
                SELECT *
                FROM wishbone."login"
                WHERE username = '{username}';
                """

    user_data = pd.read_sql_query(check_query, conn)

    if user_data.empty:
        return False

    user_dict = user_data.to_dict('series')

    if len(user_dict.get('login_id')) == 1:
        stored_hash = bytes(user_dict.get(
            'password_hash')[0], encoding='utf-8')
        return bcrypt.checkpw(password, stored_hash)

    raise LookupError('Something dreadful has happened')


def hash_password(password: str) -> bytes:
    password_bytes = bytes(password, encoding='utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt)


def delete_user(username: str, conn: connection) -> None:
    delete_query = f"""
                    DELETE FROM wishbone."login"
                    WHERE username = '{username}';
                    """

    cur = conn.cursor()

    cur.execute(delete_query)

    conn.commit()

    cur.close()


def new_user(username: str, password: str, conn: connection):
    hashed_password = hash_password(password)

    insert_query = """
                    INSERT INTO wishbone."login"
                    (username, password_hash)
                    VALUES
                        (%s, %s)
                    """

    cur = conn.cursor()

    try:
        cur.execute(insert_query, (username, hashed_password.decode()))
    except:
        print("Something went wrong creating new user")

    conn.commit()

    cur.close()


async def trigger_lambda(payload: dict) -> dict:
    async with aioboto3.client('lambda') as client:
        response = await client.invoke(
            FunctionName='wishbone-tracking-lambda',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

    response_payload = await response['Payload'].read()
    return json.loads(response_payload)


def run_unsubscribe(email: str):
    payload = {
        'subscribe': 'False',
        'email': email
    }
    return asyncio.run(trigger_lambda(payload))


def run_subscribe(email: str, game_id):
    payload = {
        'subscribe': 'True',
        'email': email,
        'game_id': str(game_id)
    }
    return asyncio.run(trigger_lambda(payload))
