import streamlit as st
from os import environ
from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection

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


@st.cache_data()
def get_data(_conn: connection) -> pd.DataFrame:
    "connects to database, connects to wishbone schema and checks data is there"
    data = pd.read_sql("""set search_path to wishbone;
                       select g.game_name,l.price,p.platform_name
                                    from listing l
                                    join game g
                                    on g.game_id=l.game_id
                                    join platform p
                                    on p.platform_id=l.platform_id;""", con=_conn)
    data = data.drop_duplicates()
    return data


def filter_data(game_filter: list, conn: connection) -> pd.DataFrame:
    "filters the dataframe dependent on game selected"
    data = get_data(conn)

    data = data[data['game_name'].isin(game_filter)]
    return data


def format_data(game_filter: list, conn: connection) -> pd.DataFrame:

    data = filter_data(game_filter, conn)

    data["platform_name"] = data["platform_name"].map(
        {"gog": "GoG", "steam": "Steam"})

    data['price'] = data['price'].astype(float)/100

    data = data.rename(columns={
        "game_name": "Game",
        "price": "Price (£)",
        "platform_name": "Platform"
    })

    return data


def create_game_name_filter(conn: connection) -> list:
    "Creates a multiselect filter to filter by game name"
    games = get_data(conn)['game_name']
    games_filter = st.multiselect(
        "Select Game", games, default=None, max_selections=10)
    return games_filter


def create_current_price_metrics() -> None:
    "Creates the dashboard page to display price metrics"
    st.image(image="./wishbone logo.png")

    st.title("Welcome to Wishbone!")

    db_conn = get_connection()

    with st.sidebar:
        with st.expander(label="Select Games"):
            game_filter = create_game_name_filter(db_conn)

    data = format_data(game_filter, db_conn)
    st.dataframe(data, hide_index=True)


create_current_price_metrics()
