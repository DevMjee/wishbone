"module for creating the streamlit dashboard"
from os import environ
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection
import boto3
import awswrangler as wr

from backend import get_connection


load_dotenv()
session = boto3.Session(
    aws_access_key_id=environ["ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"],
    region_name="eu-west-2")
S3_BUCKET_NAME = environ["BUCKET_NAME"]

LOGO_IMG_PATH = "./wishbone_logo.png"
NUM_PER_PAGE = 10


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
            LAG(price,3) OVER (PARTITION BY game_id ORDER BY recording_date) as prev_price
            FROM listing
            )
            SELECT DISTINCT g.game_id, g.game_name, price_cte.price as new_price, price_cte.prev_price as old_price, price_cte.recording_date, p.platform_name
                FROM price_cte
            JOIN game g on
                price_cte.game_id = g.game_id
            join platform p on
                price_cte.platform_id = p.platform_id
            WHERE price < prev_price"""

    game_id_df = wr.athena.read_sql_query(
        athena_query, database="wishbone-glue-db", boto3_session=session)

    game_id_df = game_id_df.drop_duplicates('game_name')

    return game_id_df


def create_price_drop_old_data(data: pd.DataFrame) -> pd.DataFrame:
    "function to create a dataframe with the column 'price' set as the old data"
    format_data_old = data.copy()
    format_data_old['old_price'] = format_data_old['old_price'].astype(
        float)/100
    format_data_old['price'] = format_data_old['old_price']
    format_data_old["dataset"] = "Old Price"

    return format_data_old


def create_price_drop_new_data(data: pd.DataFrame) -> pd.DataFrame:
    "function to create a dataframe with the column 'price' set as the new price"
    format_data_new = data.copy()
    format_data_new['new_price'] = format_data_new["new_price"].astype(
        float)/100
    format_data_new['price'] = format_data_new['new_price']
    format_data_new["dataset"] = "New Price"

    return format_data_new


def create_discount_column(data: pd.DataFrame) -> pd.DataFrame:
    "function to create a column for discount percentage"
    data = data.copy()
    data['discount'] = (1 - data['new_price']/data['old_price'])*100

    return data


def filter_data(game_filter: list, conn: connection) -> pd.DataFrame:
    "filters the dataframe dependent on game selected"
    data = check_if_game_dropped_price(conn).copy()

    data = data[data['game_name'].isin(game_filter)]
    return data


def format_data(game_filter: list, conn: connection, sort_by, sort_dir) -> pd.DataFrame:
    "Formats the dataframe for display"

    data = filter_data(game_filter, conn).copy()

    data = create_discount_column(data)

    data['old_price'] = data['old_price'].astype(float)/100

    data['new_price'] = data['new_price'].astype(float)/100

    data["platform_name"] = data["platform_name"].map(
        {"gog": "GoG", "steam": "Steam"})

    data = data[["game_name", "old_price",
                 "new_price", "discount", "platform_name"]]

    data = data.rename(columns={
        "game_name": "Game",
        "platform_name": "Platform",
        "discount": "Discount",
        "old_price": "Old Price (£)",
        "new_price": "Price"
    })

    sort_dir = sort_dir in ["Ascending"]

    data = data.sort_values(by=sort_by, ascending=sort_dir)

    data = data.rename(columns={
        "Price": "Price (£)",
        "Discount": "Discount (%)"
    })

    return data


def create_game_name_filter(conn: connection) -> list:
    "Creates a multiselect filter to filter by game name"
    games = check_if_game_dropped_price(conn)['game_name']
    games_filter = st.multiselect(
        "Select Game", games, default=games)
    return games_filter


def create_discount_filter() -> list:
    "creates a filter that allows number input to filter by minimum discount"
    discount_filter = st.number_input(
        label="Enter minimum discount percentage", max_value=100.0)
    return discount_filter


def create_paginated_df(conn: connection, game_filter, page_num, sort_by, sort_dir):
    "uses session state to create a dataframe with pages"
    unpaged_df = format_data(game_filter, conn, sort_by, sort_dir)

    start = page_num * NUM_PER_PAGE
    end = (1+page_num) * NUM_PER_PAGE

    paged_df = unpaged_df[start:end]

    return paged_df


def create_sorting_choice_filter() -> str:
    "function to allow user to choose a parameter to sort the dataframe by"

    option = st.selectbox(label="Sort By", options=[
                          "Discount", "Price"])
    return option


def create_direction_sorting_filter() -> str:
    "function to create an option to sort by price ascending or descending"
    option = st.radio(label='Order by', options=[
                      'Descending', 'Ascending'], label_visibility='hidden')
    return option


def increment_page() -> None:
    "function to increment the session state by 1"
    st.session_state.page += 1


def decrement_page() -> None:
    "function to decrement the session state by 1"
    st.session_state.page -= 1


def create_current_price_metrics() -> None:
    "Creates the dashboard page to display price metrics"

    # using columns to format the positioning of buttons on the dashboard
    # the _ defines the spacing between the tracker and login columns as 10 units
    tracker, _, login = st.columns([3, 10, 3])

    if login.button(":blue[Login]"):
        st.switch_page("./pages/2_login.py")

    if tracker.button(":blue[Game Tracker]"):

        st.switch_page("pages/1_tracker.py")

    st.image(image=LOGO_IMG_PATH)

    st.title(":grey[Welcome to Wishbone!]")

    db_conn = get_connection()

    with st.sidebar:
        with st.expander(label="Select Games"):
            game_filter = create_game_name_filter(db_conn)

            sort_by = create_sorting_choice_filter()
            sort_dir = create_direction_sorting_filter()

    data = format_data(game_filter, db_conn, sort_by, sort_dir)
    last_page = len(data)//15

    # using columns to format the positioning of buttons on the dashboard
    prev_button, _, next_button = st.columns([3, 10, 3])

    if 'page' not in st.session_state:
        st.session_state.page = 0

    page_num = st.session_state.page

    if next_button.button(":blue[Next]", on_click=increment_page):

        if st.session_state.page > last_page:
            st.session_state.page = 0

        page_num = st.session_state.page

    if prev_button.button(":blue[Previous]", on_click=decrement_page):

        if st.session_state.page < 0:
            st.session_state.page = last_page

        page_num = st.session_state.page

    df = create_paginated_df(db_conn, game_filter, page_num, sort_by, sort_dir)

    st.dataframe(df, hide_index=True, column_config={
        "Price (£)": st.column_config.NumberColumn(format="%.2f"),
        "Old Price (£)": st.column_config.NumberColumn(format="%.2f"),
        "Discount (%)": st.column_config.NumberColumn(format="%.0f")
    })


create_current_price_metrics()
