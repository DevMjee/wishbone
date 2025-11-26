import streamlit as st
from backend import (validate_login, validate_new_email,
                     validate_new_password, validate_new_username,
                     check_login, create_user,
                     get_connection)


def run_login(conn):
    """Displays the login prompt and logs a user in"""
    identity = st.text_input('Username or email')
    password = bytes(st.text_input(
        'Password', type='password'), encoding='utf-8')

    if st.button(label='Login'):
        validation = validate_login(identity, password)

        if not validation.get('success'):
            st.text(validation.get('msg'))

        else:
            response = check_login(identity, password, conn)
            st.text(response.get('msg'))

            if response.get('success'):
                print('logged in')
                # TODO USER IS LOGGED IN, DO LOGGED IN THINGS (Session state)


def run_create_account(conn):
    """Displays the create account prompt and creates a user with provided info"""
    email = st.text_input('Enter your email')

    e_validation = validate_new_email(email, conn)
    st.text(e_validation.get('msg'))

    username = st.text_input('Choose a username')

    u_validation = validate_new_username(username, conn)
    st.text(u_validation.get('msg'))

    if u_validation.get('success') and e_validation.get('success'):
        password_1 = st.text_input('New Password', type='password')
        password_2 = st.text_input('Confirm Password', type='password')

        if st.button('Create account'):
            p_validation = validate_new_password(
                password_1, password_2)
            st.text(p_validation.get('msg'))

            if p_validation.get('success'):
                response = create_user(username, email, password_1, conn)
                st.text(response.get('msg'))


def login():
    "Runs the login page"
    tracker, _, home = st.columns([3, 10, 3])

    if tracker.button("Game Tracker"):
        st.switch_page("pages/1_Game Tracker.py")

    if home.button("Home"):
        st.switch_page("./Homepage.py")

    db_conn = get_connection()

    if "create_account" not in st.session_state:
        st.session_state.create_account = False

    if st.session_state.create_account:
        run_create_account(db_conn)
        if st.button("Back to login"):
            st.session_state.create_account = False
            st.rerun()

    else:
        run_login(db_conn)
        if st.button("Don't have an account? Click here!"):
            st.session_state.create_account = True
            st.rerun()


login()
