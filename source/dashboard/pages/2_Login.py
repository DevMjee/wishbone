import streamlit as st
from backend import (validate_login, validate_new_email,
                     validate_new_password, validate_new_username,
                     check_login, create_user,
                     get_connection, validate_email,
                     get_user_data_by_email,
                     get_user_data_by_username, delete_user,
                     EmailNotValidError)


def run_login(conn):
    """Displays the login prompt and logs a user in"""
    identity = st.text_input('Username or email')
    password = bytes(st.text_input(
        'Password', type='password'), encoding='utf-8')

    if not st.button(label='Login'):
        return

    validation = validate_login(identity, password)

    if not validation.get('success'):
        st.text(validation.get('msg'))
        return

    response = check_login(identity, password, conn)
    st.text(response.get('msg'))

    if not response.get('success'):
        return

    print('Logged in. You will be redirected shortly')
    st.session_state.logged_in = True

    try:
        validate_email(identity)
        user_data = get_user_data_by_email(identity, conn)
    except EmailNotValidError:
        user_data = get_user_data_by_username(identity, conn)

    st.session_state.username = user_data.to_dict('series').get('username')[0]
    st.session_state.email = user_data.to_dict('series').get('email')[0]
    st.rerun()


def run_create_account(conn):
    """Displays the create account prompt and creates a user with provided info"""
    email = st.text_input('Enter your email')

    e_validation = validate_new_email(email, conn)
    st.text(e_validation.get('msg'))

    username = st.text_input('Choose a username')

    u_validation = validate_new_username(username, conn)
    st.text(u_validation.get('msg'))

    if st.button('Continue'):
        st.rerun()

    if not (u_validation.get('success') and e_validation.get('success')):
        return

    password_1 = st.text_input('New Password', type='password')
    password_2 = st.text_input('Confirm Password', type='password')

    if not st.button('Create account'):
        return
    p_validation = validate_new_password(
        password_1, password_2)
    st.text(p_validation.get('msg'))

    if not p_validation.get('success'):
        return

    response = create_user(username, email, password_1, conn)
    st.text(response.get('msg'))


def login(conn):
    "Runs the login page"
    tracker, _, home = st.columns([3, 10, 3])

    if tracker.button("Game Tracker"):
        st.switch_page("pages/1_Game Tracker.py")

    if home.button("Home"):
        st.switch_page("./Homepage.py")

    if "create_account" not in st.session_state:
        st.session_state.create_account = False

    if st.session_state.create_account:
        run_create_account(conn)
        if st.button("Back to login"):
            st.session_state.create_account = False
            st.rerun()

    else:
        run_login(conn)
        if st.button("Don't have an account? Click here!"):
            st.session_state.create_account = True
            st.rerun()


def logout():
    st.session_state.username = ''
    st.session_state.email = ''
    st.session_state.logged_in = False
    st.rerun()


def account(conn):
    if 'deleting' not in st.session_state:
        st.session_state.deleting = False

    st.title(f'You are logged in as {st.session_state.username}')
    st.text(st.session_state.email)
    if st.button('Logout'):
        logout()

    if st.button('Delete account'):
        st.session_state.deleting = True

    if st.session_state.deleting:
        st.text(
            'Are you sure you want to delete your account? This action is permanent.')
        if st.button('Yes'):
            delete_user(st.session_state.username, conn)
            logout()
            st.session_state.deleting = False
            st.rerun()

        if st.button('No'):
            st.session_state.deleting = False
            st.rerun()


if __name__ == "__main__":
    db_conn = get_connection()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login(db_conn)
    else:
        account(db_conn)
