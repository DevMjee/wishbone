import streamlit as st
from backend import (validate_login, validate_new_email,
                     validate_new_password, validate_new_username,
                     check_login, create_user,
                     get_connection)


def run_login(conn):
    identity = st.text_input('Username or email')
    password = bytes(st.text_input('Password'), encoding='utf-8')

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
    email = st.text_input('Enter your email')
    e_validation = validate_new_email(email, conn)
    st.text(e_validation.get('msg'))
    username = st.text_input('Choose a username')
    u_validation = validate_new_username(username, conn)
    st.text(u_validation.get('msg'))

    if u_validation.get('success') and e_validation.get('success'):
        password_1 = st.text_input('New Password')
        password_2 = st.text_input('Confirm Password')

        if st.button('Create account'):
            p_validation = validate_new_password(
                password_1, password_2)

            st.text(p_validation.get('msg'))

            if p_validation.get('success'):
                response = create_user(username, email, password_1, conn)
                st.text(response.get('msg'))


db_conn = get_connection()

# Initialize session state variable
if "create_account" not in st.session_state:
    st.session_state.create_account = False

# Button to switch modes
if st.button("Don't have an account? Click here!"):
    st.session_state.create_account = True

# Show appropriate form
if st.session_state.create_account:
    run_create_account(db_conn)
else:
    run_login(db_conn)
