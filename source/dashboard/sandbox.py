import pandas as pd
import bcrypt
from os import environ
from psycopg2 import connect
from psycopg2.extensions import connection
from dotenv import load_dotenv


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


def hash_password(password: str) -> bytes:
    password_bytes = bytes(password, encoding='utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt)


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


def delete_user(username: str, conn: connection) -> None:
    delete_query = f"""
                    DELETE FROM wishbone."login"
                    WHERE username = '{username}';
                    """

    cur = conn.cursor()

    cur.execute(delete_query)

    conn.commit()

    cur.close()


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


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    #  new_user('adam', '1234', conn)
    # delete_user('adam', conn)
    print(check_login('adam', bytes('1234', encoding='utf-8'), conn))
    print(check_login('adam', bytes('1234', encoding='utf-8'), conn))
    print(check_login('adam', bytes('1234', encoding='utf-8'), conn))
    print(check_login('adam', bytes('1234', encoding='utf-8'), conn))
