"""Code for the Streamlit dashboard"""
import streamlit as st
import boto3
import awswrangler as wr
from os import environ
from dotenv import load_dotenv
import altair as alt
import pandas as pd
from backend import run_unsubscribe

load_dotenv()
session = boto3.Session(
    aws_access_key_id=environ["ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY_ID"],
    region_name="eu-west-2")
S3_BUCKET_NAME = environ["BUCKET_NAME"]


@st.cache_data()
def get_data():
    data = wr.athena.read_sql_query("""
    select g.game_name, l.price, l.recording_date
                                    from listing l
                                    join game g
                                    on g.game_id=l.game_id
""", database='wishbone-glue-db')

    data = data.rename(columns={
        "game_name": "Game",
    })

    return data


def unsub_button():
    email = st.text_input('Email', "example@domain.com", )
    unsub = st.button(
        label='Unsubscribe from all',
        help='click to remove your email from our system'
    )
    response = {'status': 'success', 'msg': ''}
    if unsub:
        response = run_unsubscribe(email)

    return response


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


def create_dashbaord():

    st.set_page_config(page_title="Game Tracker", page_icon="👻")

    with st.sidebar:
        with st.expander(label="Choose Games to Track"):
            game_filter = create_game_name_filter()
    chart = create_price_vs_time_chart(game_filter)
    st.altair_chart(chart)
    response = unsub_button()
    st.text(response.get('msg'))
    print(response)


create_dashbaord()
