from streamlit.testing.v1 import AppTest

at = AppTest.from_file('Homepage.py', default_timeout=10)


def test_homepage_runs():
    at.run()
    assert not at.exception
