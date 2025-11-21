"""Code for the Streamlit dashboard"""
import streamlit as st
import boto3
import aioboto3
import awswrangler as wr
from os import environ
from dotenv import load_dotenv
import altair as alt
import json
import asyncio

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


async def trigger_unsubscribe(email: str) -> None:
    payload_unsubscribe = {
        'subscribe': 'False',
        'email': email
    }
    async with aioboto3.client('lambda') as client:
        response = await client.invoke(
            FunctionName='wishbone-tracking-lambda',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload_unsubscribe)
        )

    response_payload = await response['Payload'].read()
    return json.loads(response_payload)


def run_unsubscribe(email: str):
    return asyncio.run(trigger_unsubscribe(email))


def subscription():
    email = st.text_input('Email', "example@domain.com", )
    unsub = st.button(
        label='Unsubscribe from all',
        help='click to remove your email from our system'
    )
    response = {'status': 'success', 'msg': 'button not pressed yet'}
    if unsub:
        response = run_unsubscribe(email)

    return response


def create_price_vs_time_chart(game_filter):
    data = get_data()

    data = data[data['Game'].isin(game_filter)]
    chart = alt.Chart(data).mark_line().encode(
        alt.X("recording_date", title="Date"),
        alt.Y("price", title="Price"),
        alt.Color("Game:N")


    )
    return chart


def create_game_name_filter():
    games = get_data()['Game']
    games_filter = st.multiselect("Select Game", games, default=None)
    return games_filter


def create_dashbaord():

    with st.sidebar:
        game_filter = create_game_name_filter()
    chart = create_price_vs_time_chart(game_filter)
    st.altair_chart(chart)
    response = subscription()
    st.text(response)


if __name__ == "__main__":
    create_dashbaord()
