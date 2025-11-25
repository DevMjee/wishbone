import aioboto3
import json
import asyncio
from psycopg2 import connect
from psycopg2.extensions import connection
from psycopg2.errors import UniqueViolation
import bcrypt
import pandas as pd
from os import environ
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError

load_dotenv()


def get_connection() -> connection:
    "function to return connection to the RDS database"
    conn = connect(
        host=environ["RDS_HOST"],
        user=environ["RDS_USERNAME"],
        password=environ["RDS_PASSWORD"],
        dbname=environ["DB_NAME"],
        port=environ["PORT"],
    )

    return conn


def get_user_data_by_username(username: str, conn: connection) -> pd.DataFrame:
    check_query = f"""
                SELECT *
                FROM wishbone."login"
                JOIN wishbone."users"
                    USING(user_id)
                WHERE username = '{username}';
                """

    return pd.read_sql_query(check_query, conn)


def get_user_data_by_email(email: str, conn: connection) -> pd.DataFrame:
    check_query = f"""
                SELECT *
                FROM wishbone."login"
                JOIN wishbone."users"
                    USING(user_id)
                WHERE email = '{email}';
                """

    return pd.read_sql_query(check_query, conn)


def check_login(identity: str, password: bytes, conn: connection) -> dict:
    try:
        validate_email(identity)
        user_data = get_user_data_by_email(identity, conn)

    except EmailNotValidError:
        user_data = get_user_data_by_username(identity, conn)

    if user_data.empty:
        return {'success': False, 'msg': f"User '{identity}' is not recognised."}

    user_dict = user_data.to_dict('series')

    if not len(user_dict.get('login_id')) == 1:
        return {'success': False, 'msg': f"What manner of thing has occured??? \
                (Multiple entries returned for user '{identity}'.)"}

    stored_hash = bytes(user_dict.get(
        'password_hash')[0], encoding='utf-8')

    if not bcrypt.checkpw(password, stored_hash):
        return {'success': False, 'msg': 'Password is incorrect.'}

    return {'success': True, 'msg': 'Logged in successfully.'}


def hash_password(password: str) -> bytes:
    password_bytes = bytes(password, encoding='utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt)


def delete_user(username: str, conn: connection) -> None:
    delete_query = f"""
                    DELETE FROM wishbone."login"
                    JOIN wishbone."users"
                        USING(user_id)
                    WHERE username = '{username}';
                    """

    cur = conn.cursor()

    cur.execute(delete_query)

    conn.commit()

    cur.close()


def validate_login(identity: str, password: str) -> dict:
    if not identity:
        return {'success': False, 'msg': 'Username or email cannot be blank.'}

    if not password:
        return {'success': False, 'msg': 'Password cannot be blank.'}

    return {'success': True, 'msg': 'Username and password are present.'}


def validate_new_password(password_1: str, password_2: str) -> dict:
    # TODO: Add more strict password rules
    if not password_1:
        return {'success': False, 'msg': 'Password cannot be blank.'}

    if not len(password_1) >= 8:
        return {'success': False, 'msg': 'Password must be at least 8 characters long.'}

    if not password_1 == password_2:
        return {'success': False, 'msg': 'Passwords do not match.'}

    return {'success': True, 'msg': 'Passwords match.'}


def validate_new_username(username: str, conn: connection) -> dict:
    # TODO: Add more strict username rules
    if not username:
        return {'success': False, 'msg': 'Username cannot be blank.'}

    if not username.isascii():
        return {'success': False, 'msg': 'Username cannot contain non-ASCII characters'}

    if not username.replace('_', '').isalnum():
        return {'success': False, 'msg': 'Username can contain only letters and numbers'}

    if not len(username) >= 3:
        return {'success': False, 'msg': 'Username must be at least 3 characters long.'}

    user_data = get_user_data_by_username(username, conn)
    if not user_data.empty:
        return {'success': False, 'msg': f"User '{username}' already exists."}

    return {'success': True, 'msg': 'This username is available.'}


def validate_new_email(email: str, conn: connection) -> dict:
    try:
        validate_email(email)

    except EmailNotValidError:
        return {'success': False, 'msg': 'Please enter a valid email address.'}

    user_data = get_user_data_by_email(email, conn)
    if not user_data.empty:
        return {'success': False, 'msg': 'There is already an account associated with this email address.'}

    return {'success': True, 'msg': 'This email is valid.'}


def create_user(username: str, email: str, password: str, conn: connection) -> dict:
    hashed_password = hash_password(password)
    insert_users_query = """
                    INSERT INTO wishbone."users"
                        (username, email)
                    VALUES
                        (%s, %s)
                    RETURNING user_id
                        """

    insert_login_query = """
                    INSERT INTO wishbone."login"
                    (user_id, password_hash)
                    VALUES
                        (%s, %s)
                    """

    cur = conn.cursor()
    try:
        cur.execute(insert_users_query, (username, email))
        user_id = cur.fetchone()[0]

    except UniqueViolation as e:
        return {'success': False, 'msg': str(e)}

    try:
        cur.execute(insert_login_query, (user_id, hashed_password.decode()))

    except UniqueViolation as e:
        return {'success': False, 'msg': str(e)}

    conn.commit()

    cur.close()

    return {'success': True, 'msg': 'Account created successfully!'}


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
