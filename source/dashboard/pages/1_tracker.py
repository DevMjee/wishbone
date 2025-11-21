"""Code for the Streamlit dashboard"""
import streamlit as st
import boto3
import awswrangler as wr
from os import environ
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from backend import run_unsubscribe
from backend import run_subscribe

load_dotenv()
session = boto3.Session(
    aws_access_key_id=environ["ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"],
    region_name="eu-west-2")
S3_BUCKET_NAME = environ["BUCKET_NAME"]


@st.cache_data()
def get_data():
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


def unsub_button(email):

    unsub = st.button(
        label='Unsubscribe from all',
        help='click to remove your email from our system'
    )
    response = {'status': 'idle', 'msg': 'button not pressed'}
    if unsub:
        response = run_unsubscribe(email)

    return response


def sub_selects():
    games = get_data()['Game']
    sub = st.multiselect(
        label="Select Games to subscribe to",
        options=games
    )
    return sub


def sub_button(email, games):
    game_ids = get_data()[['game_id', 'Game']]
    filtered_ids = game_ids[game_ids['Game'].isin(games)]
    sub = st.button(
        label="Subscribe to the selected games"
    )
    response = {'status': 'success', 'msg': ''}
    if sub:
        for game_id in filtered_ids["game_id"]:
            run_subscribe(email, game_id)


def create_price_vs_time_chart(game_filter):
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


def create_game_name_filter():
    games = get_data()['Game'].unique()

    games_filter = st.multiselect(
        "Select Game", games, default=None, max_selections=10)
    return games_filter


def create_dashboard():

    st.set_page_config(page_title="Game Tracker", page_icon="👻")

    with st.sidebar:
        with st.expander(label="Choose Games to Track"):
            game_filter = create_game_name_filter()
    chart = create_price_vs_time_chart(game_filter)
    st.altair_chart(chart)

    email = st.text_input('Email', "example@domain.com", )
    games = sub_selects()
    sub_button(email, games)
    response = unsub_button(email)
    if not response.get('status') == 'idle':
        st.text(response.get('msg'))

    print(response)


create_dashboard()
