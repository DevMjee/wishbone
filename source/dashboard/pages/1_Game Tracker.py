"""Code for the Streamlit dashboard"""
import streamlit as st
<<<<<<< HEAD
=======
import boto3
>>>>>>> d109735 (trying to fix missing file changes on pr)
import awswrangler as wr
from os import environ
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from backend import run_unsubscribe, run_subscribe, get_boto3_session
<<<<<<< HEAD
import aioboto3
import json
import asyncio
=======
>>>>>>> d109735 (trying to fix missing file changes on pr)


@st.cache_data()
def get_data() -> pd.DataFrame:
<<<<<<< HEAD
    """queries the Glue DB and returns game data"""
    data = wr.athena.read_sql_query("""
    SELECT 
        g.game_id,g.game_name, l.price, l.recording_date, p.platform_name
    FROM 
        listing l
    JOIN 
        game g
    ON 
        g.game_id=l.game_id
    JOIN 
        platform p
    ON 
        p.platform_id=l.platform_id
=======
    "queries the Glue DB and returns game data"
    data = wr.athena.read_sql_query("""
    select g.game_id,g.game_name, l.price, l.recording_date, p.platform_name
                                    from listing l
                                    join game g
                                    on g.game_id=l.game_id
                                    join platform p
                                    on p.platform_id=l.platform_id
>>>>>>> d109735 (trying to fix missing file changes on pr)
                                    
""", database='wishbone-glue-db', boto3_session=session)

    data = data.rename(columns={
        "game_name": "Game",
    })
    data = data.drop_duplicates()
    return data


<<<<<<< HEAD
def sub_selection() -> list:
    """multiselect option to select games to subscribe to"""
=======
def sub_selects() -> list:
    "multiselect option to select games to subscribe to"
>>>>>>> d109735 (trying to fix missing file changes on pr)
    games = get_data()['Game']
    sub = st.multiselect(
        label="Select Games to subscribe to",
        options=games
    )
    return sub


def sub_button(email: str, games: list) -> None:
<<<<<<< HEAD
    """button to subscribe to all games selected in sub_selects"""
=======
    "button to subscribe to all games selected in sub_selects"
>>>>>>> d109735 (trying to fix missing file changes on pr)
    game_ids = get_data()[['game_id', 'Game']]
    filtered_ids = game_ids[game_ids['Game'].isin(games)]
    sub = st.button(
        label="Subscribe to the selected games"
    )
    if sub:
        for game_id in filtered_ids["game_id"]:
            run_subscribe(email, game_id)


def create_price_vs_time_chart(game_filter: list) -> alt.Chart:
<<<<<<< HEAD
    """creates a price vs time chart for every selected game"""
=======
    "creates a price vs time chart for every selected game"
>>>>>>> d109735 (trying to fix missing file changes on pr)
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
<<<<<<< HEAD
    """create filter to filter the data for the graph by game name"""
=======
    "create filter to filter the data for the graph by game name"
>>>>>>> d109735 (trying to fix missing file changes on pr)
    games = get_data()['Game'].unique()

    games_filter = st.multiselect(
        "Select Game", games, default=None, max_selections=10)
    return games_filter


def account_button():
    _, _, user = st.columns([3, 10, 3])
    with user.expander(st.session_state.username):
        if st.button('Account'):
            st.switch_page("pages/2_Login.py")


<<<<<<< HEAD
async def trigger_search_lambda(payload: dict) -> dict:
    """triggers the lambda for mailing list subscription"""
    async with aioboto3.client('lambda') as client:
        response = await client.invoke(
            FunctionName='wishbone-search-lambda',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

    response_payload = await response['Payload'].read()
    return json.loads(response_payload)


def create_dashboard() -> None:
    """calls all of the above functions to create the tracking page of the dashboard"""
=======
def create_dashboard() -> None:
    "calls all of the above functions to create the tracking page of the dashboard"
>>>>>>> d109735 (trying to fix missing file changes on pr)
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

<<<<<<< HEAD
            search = st.text_input(
                label="Would you like to add a game to our tracking?")
            if game_filter is not None and game_filter != []:
                st.session_state['game_filter'] = game_filter
    if search:
        lambda_name_input = {"game_inputs": search}
        asyncio.run(trigger_search_lambda(lambda_name_input))
=======
            if game_filter is not None and game_filter != []:
                st.session_state['game_filter'] = game_filter
>>>>>>> d109735 (trying to fix missing file changes on pr)

    if 'game_filter' not in st.session_state:
        st.session_state['game_filter'] = []

    game_filter = st.session_state.get("game_filter", [])
    chart = create_price_vs_time_chart(st.session_state.game_filter)
    st.altair_chart(chart)

    if 'email' in st.session_state:
        email = st.text_input('Email', st.session_state.email)

    else:
        email = st.text_input('Email')

<<<<<<< HEAD
    games = sub_selection()
=======
    games = sub_selects()
>>>>>>> d109735 (trying to fix missing file changes on pr)
    sub_button(email, games)

    if st.button('Unsubscribe from all'):
        run_unsubscribe(email)


if __name__ == "__main__":
    load_dotenv()
    session = get_boto3_session()
    create_dashboard()
