"module for creating the streamlit dashboard"
from os import environ
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import awswrangler as wr
from backend import get_boto3_session


S3_BUCKET_NAME = environ["BUCKET_NAME"]

LOGO_IMG_PATH = "https://raw.githubusercontent.com/DevMjee/wishbone/refs/heads/main/assets/logo.png"
NUM_PER_PAGE = 10


@st.cache_data()
def create_max_price_column() -> pd.DataFrame:
    query = """
        with price_cte as (select game_id, price, recording_date, platform_id, max(price) over (partition by game_id) as max_price
        from listing)
        select g.game_name, price_cte.recording_date, price_cte.price, p.platform_name, price_cte.max_price
        from price_cte
        join game g 
        on price_cte.game_id = g.game_id
        join platform p 
        on price_cte.platform_id = p.platform_id
        where price_cte.price < price_cte.max_price
        order by price_cte.recording_date desc
        
"""
    game_id_df = wr.athena.read_sql_query(
        query, database="wishbone-glue-db", boto3_session=session)

    game_id_df = game_id_df.drop_duplicates('game_name')

    return game_id_df


def create_discount_column(data: pd.DataFrame) -> pd.DataFrame:
    "function to create a column for discount percentage"
    data = data.copy()
    data['discount'] = (1 - data['price']/data['max_price'])*100
    data = data[data["discount"] > 0.0]

    return data


def filter_data(game_filter: list, data: pd.DataFrame) -> pd.DataFrame:
    "filters the dataframe dependent on game selected"

    data = data[data['game_name'].isin(game_filter)]
    return data


def format_data(game_filter: list, sort_by: str, sort_dir: str, data: pd.DataFrame) -> pd.DataFrame:
    "Formats the dataframe for display"

    filtered_data = filter_data(game_filter, data).copy()

    filtered_data = create_discount_column(filtered_data)

    filtered_data['max_price'] = filtered_data['max_price'].astype(float)/100

    filtered_data['price'] = filtered_data['price'].astype(float)/100

    filtered_data["platform_name"] = filtered_data["platform_name"].map(
        {"gog": "GoG", "steam": "Steam"})

    filtered_data = filtered_data[["game_name", "max_price",
                                   "price", "discount", "platform_name"]]

    filtered_data = filtered_data.rename(columns={
        "game_name": "Game",
        "platform_name": "Platform",
        "discount": "Discount",
        "max_price": "Old Price (£)",
        "price": "Price"
    })

    sort_dir = sort_dir in ["Ascending"]

    filtered_data = filtered_data.sort_values(by=sort_by, ascending=sort_dir)

    filtered_data = filtered_data.rename(columns={
        "Price": "Price (£)",
        "Discount": "Discount (%)"
    })

    return filtered_data


def create_game_name_filter(data: pd.DataFrame) -> list:
    "Creates a multiselect filter to filter by game name"
    games = data['game_name'].copy()
    games = games.drop_duplicates()
    games_filter = st.multiselect(
        "Select Game", games, default=games)
    return games_filter


def create_paginated_df(page_num: int, data: pd.DataFrame) -> pd.DataFrame:
    "uses session state to create a dataframe with pages"

    start = page_num * NUM_PER_PAGE
    end = (1+page_num) * NUM_PER_PAGE

    paged_df = data[start:end]

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


def account_button():
    _, _, user = st.columns([3, 10, 3])
    with user.expander(st.session_state.username):
        if st.button('Account'):
            st.switch_page("pages/2_Login.py")


def create_current_price_metrics() -> None:
    "Creates the dashboard page to display price metrics"

    # using columns to format the positioning of buttons on the dashboard
    # the _ defines the spacing between the tracker and login columns as 10 units
    if 'username' in st.session_state:
        account_button()
    tracker, _, login = st.columns([3, 10, 3])

    if login.button(":blue[Login]"):
        st.switch_page("./pages/2_Login.py")

    if tracker.button(":blue[Game Tracker]"):

        st.switch_page("pages/1_Game Tracker.py")

    st.image(image=LOGO_IMG_PATH)

    st.title(":grey[Welcome to Wishbone!]")

    glue_data = create_max_price_column()

    with st.sidebar:
        with st.expander(label="Select Games"):
            game_filter = create_game_name_filter(glue_data)

            sort_by = create_sorting_choice_filter()
            sort_dir = create_direction_sorting_filter()

    data = format_data(game_filter, sort_by, sort_dir, glue_data)
    last_page = len(data)//NUM_PER_PAGE

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

    df = create_paginated_df(page_num, data)

    st.dataframe(df, hide_index=True, column_config={
        "Price (£)": st.column_config.NumberColumn(format="%.2f"),
        "Old Price (£)": st.column_config.NumberColumn(format="%.2f"),
        "Discount (%)": st.column_config.NumberColumn(format="%.0f")
    })


if __name__ == "__main__":
    load_dotenv()
    session = get_boto3_session()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    create_current_price_metrics()
