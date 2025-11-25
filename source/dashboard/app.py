import streamlit as st
from os import environ
from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection
import boto3
import awswrangler as wr
import altair as alt


load_dotenv()
session = boto3.Session(
    aws_access_key_id=environ["ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"],
    region_name="eu-west-2")
S3_BUCKET_NAME = environ["BUCKET_NAME"]


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
def get_rds_data(_conn: connection) -> pd.DataFrame:
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


@st.cache_data()
def get_glue_db_data() -> pd.DataFrame:
    "queries the Glue DB and returns game data"
    data = wr.athena.read_sql_query("""
    select g.game_id,g.game_name, l.price, l.recording_date, p.platform_name
                                    from listing l
                                    join game g
                                    on g.game_id=l.game_id
                                    join platform p
                                    on p.platform_id=l.platform_id
                                    
""", database='wishbone-glue-db')

    data = data.rename(columns={
        "game_name": "Game",
    })
    data = data.drop_duplicates()
    return data


@st.cache_data()
def check_if_game_dropped_price(_conn: connection) -> pd.DataFrame:
    "checks through the Glue DB data to see if any games have dropped in price"

    athena_query = """WITH price_cte AS (
            SELECT game_id, recording_date, price, platform_id,
            LAG(price) OVER (PARTITION BY game_id ORDER BY recording_date) as prev_price
            FROM listing
            )
            SELECT DISTINCT g.game_id, g.game_name, price_cte.price as new_price, price_cte.prev_price as old_price, price_cte.recording_date, p.platform_name
                FROM price_cte
            JOIN game g on
                price_cte.game_id = g.game_id
            join platform p on
                price_cte.platform_id = p.platform_id
            WHERE price < prev_price"""

    session = boto3.Session(aws_access_key_id=environ["ACCESS_KEY_ID"],
                            aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"], region_name='eu-west-2')

    game_id_df = wr.athena.read_sql_query(
        athena_query, database="wishbone-glue-db", boto3_session=session)

    return game_id_df


def create_price_drop_old_data(data: pd.DataFrame):

    format_data_old = data.copy()
    format_data_old['price'] = format_data_old['old_price'].astype(float)/100
    format_data_old["dataset"] = "Old Price"

    return format_data_old


def create_price_drop_new_data(data: pd.DataFrame):

    format_data_new = data.copy()
    format_data_new['price'] = format_data_new["new_price"].astype(float)/100
    format_data_new["dataset"] = "New Price"

    return format_data_new


def filter_data(game_filter: list, conn: connection) -> pd.DataFrame:
    "filters the dataframe dependent on game selected"
    data = get_rds_data(conn)

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
    games = get_rds_data(conn)['game_name']
    games_filter = st.multiselect(
        "Select Game", games, default=games)
    return games_filter


def create_discount_filter() -> list:

    discount_filter = st.number_input(
        label="Enter minimum discount percentage", max_value=100.0)
    return discount_filter


def create_paginated_df(conn: connection, game_filter, page_num):

    num_per_page = 15
    unpaged_df = format_data(game_filter, conn)

    start = page_num * num_per_page
    end = (1+page_num) * num_per_page

    paged_df = unpaged_df[start:end]

    return paged_df


def increment_page():

    st.session_state.page += 1


def decrement_page():
    st.session_state.page -= 1


def create_current_price_metrics() -> None:
    "Creates the dashboard page to display price metrics"
    st.image(image="./wishbone logo.png")

    st.title("Welcome to Wishbone!")

    db_conn = get_connection()

    with st.sidebar:
        with st.expander(label="Select Games"):
            game_filter = create_game_name_filter(db_conn)

        discount = create_discount_filter()

    price_drop_data = check_if_game_dropped_price(db_conn)
    price_drop_data = price_drop_data[price_drop_data['new_price'] <= (
        1-discount/100)*price_drop_data['old_price']]
    old_data = create_price_drop_old_data(price_drop_data)
    new_data = create_price_drop_new_data(price_drop_data)
    combined = pd.concat([old_data, new_data])
    price_drop_chart = alt.Chart(combined).mark_bar().encode(
        alt.X("price", axis=alt.Axis(orient='top'), title='Price'),
        alt.Y("game_name", title='Game'),
        alt.Color("dataset:N"),

        yOffset="dataset:N"
    )

    data = format_data(game_filter, db_conn)
    last_page = len(data)//15

    prev, _, next = st.columns([3, 10, 3])

    if 'page' not in st.session_state:
        st.session_state.page = 0

    page_num = st.session_state.page

    if next.button("Next", on_click=increment_page):

        if st.session_state.page > last_page:
            st.session_state.page = 0

        page_num = st.session_state.page

    if prev.button("Previous", on_click=decrement_page):

        if st.session_state.page < 0:
            st.session_state.page = last_page

        page_num = st.session_state.page

    df = create_paginated_df(db_conn, game_filter, page_num)

    st.dataframe(df)


create_current_price_metrics()
