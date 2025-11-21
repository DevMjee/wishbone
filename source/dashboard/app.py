import streamlit as st
import boto3
import awswrangler as wr
from os import environ
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection

load_dotenv()

st.image(image="./wishbone logo.png")

st.title("Welcome to Wishbone!")


def get_connection():
    "function to return connection to the RDS database"
    conn = connect(
        host=environ["RDS_HOST"],
        user=environ["RDS_USERNAME"],
        password=environ["RDS_PASSWORD"],
        dbname=environ["DB_NAME"],
        port=environ["PORT"],
    )

    return conn


def get_data(conn: connection):
    "connects to database, connects to wishbone schema and checks data is there"
    data = pd.read_sql("""set search_path to wishbone;
                       select g.game_name, l.price
                                    from listing l
                                    join game g
                                    on g.game_id=l.game_id;""", con=conn)
    return data


def filter_and_format_data(game_filter, conn):

    data = get_data(conn)
    data['price'] = data['price'].astype(float)/100

    data = data[data['game_name'].isin(game_filter)]

    return [data['game_name'].unique(), data['price'].unique()]


def create_game_name_filter(conn):
    games = get_data(conn)['game_name'].unique()
    games_filter = st.multiselect(
        "Select Game", games, default=None, max_selections=10)
    return games_filter


def create_current_price_metrics():

    db_conn = get_connection()

    with st.sidebar:
        with st.expander(label="Select Games"):
            game_filter = create_game_name_filter(db_conn)

    game_name, game_price = filter_and_format_data(game_filter, db_conn)
    st.metric("Game", "Current Price")
    for i in range(len(game_name)):
        st.metric(f"{game_name[i]}", f"{game_price[i]}")


create_current_price_metrics()
