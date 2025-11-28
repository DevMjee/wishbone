"""Code for the Streamlit dashboard"""
import streamlit as st
import boto3
import awswrangler as wr
from os import environ
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from backend import run_unsubscribe, run_subscribe, get_boto3_session


@st.cache_data()
def get_data() -> pd.DataFrame:
    "queries the Glue DB and returns game data"
    data = wr.athena.read_sql_query("""
    select g.game_id,g.game_name, l.price, l.recording_date, p.platform_name
                                    from listing l
                                    join game g
                                    on g.game_id=l.game_id
                                    join platform p
                                    on p.platform_id=l.platform_id
                                    
""", database='wishbone-glue-db', boto3_session=session)

    data = data.rename(columns={
        "game_name": "Game",
    })
    data = data.drop_duplicates()
    return data


def sub_selects() -> list:
    "multiselect option to select games to subscribe to"
    games = get_data()['Game']
    sub = st.multiselect(
        label="Select Games to subscribe to",
        options=games
    )
    return sub


def sub_button(email: str, games: list) -> None:
    "button to subscribe to all games selected in sub_selects"
    game_ids = get_data()[['game_id', 'Game']]
    filtered_ids = game_ids[game_ids['Game'].isin(games)]
    sub = st.button(
        label="Subscribe to the selected games"
    )
    if sub:
        for game_id in filtered_ids["game_id"]:
            run_subscribe(email, game_id)


def create_price_vs_time_chart(game_filter: list) -> alt.Chart:
    "creates a price vs time chart for every selected game"
    data = get_data()
    data['recording_date'] = data['recording_date'].dt.date
    data['price'] = data['price'].astype(float)/100
    data = data[data['Game'].isin(game_filter)]

    chart = alt.Chart(data).mark_line().encode(
        alt.X("recording_date:T", title="Date",
              axis=alt.Axis(format=r"%Y-%m-%d")),
        alt.Y("price", title="Price (£)"),
        alt.Color("Game:N")


    ).properties(title="Game Price over Time")
    return chart


def create_game_name_filter() -> list:
    "create filter to filter the data for the graph by game name"
    games = get_data()['Game'].unique()

    games_filter = st.multiselect(
        "Select Game", games, default=None, max_selections=10)
    return games_filter


def account_button():
    _, _, user = st.columns([3, 10, 3])
    with user.expander(st.session_state.username):
        if st.button('Account'):
            st.switch_page("pages/2_Login.py")


def create_dashboard() -> None:
    "calls all of the above functions to create the tracking page of the dashboard"
    st.set_page_config(page_title="Game Tracker", page_icon="🎮")

    # using columns to format the positioning of buttons on the dashboard
    if 'username' in st.session_state:
        account_button()
    home, _, login = st.columns([3, 10, 3])

    if home.button("Home"):
        st.switch_page("./Homepage.py")

    if login.button("Login"):
        st.switch_page("pages/2_Login.py")

    with st.sidebar:
        with st.expander(label="Choose Games to Track"):
            game_filter = create_game_name_filter()

            if game_filter is not None and game_filter != []:
                st.session_state['game_filter'] = game_filter

    if 'game_filter' not in st.session_state:
        st.session_state['game_filter'] = []

    game_filter = st.session_state.get("game_filter", [])
    chart = create_price_vs_time_chart(st.session_state.game_filter)
    st.altair_chart(chart)

    if 'email' in st.session_state:
        email = st.text_input('Email', st.session_state.email)

    else:
        email = st.text_input('Email')

    games = sub_selects()
    sub_button(email, games)

    if st.button('Unsubscribe from all'):
        run_unsubscribe(email)


if __name__ == "__main__":
    load_dotenv()
    session = get_boto3_session()
    create_dashboard()
