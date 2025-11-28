| Component | File | Description |
|-----------|------|-------------|
| **Homepage** | `Homepage.py` | Main page of the dashboard, containing the logo from GitHub and data from the Glue DB |
| **Game Tracker** | `pages/1_Game Tracker.py` | Game Tracker page of the dashboard, containing a graph for the game price history |
| **Login** | `pages/2_Login.py` | Login page of the dashboard, containing user input to create an account for storing wishlists |
| **Backend**| `backend.py` | Contains repeated functions to be called by the dashboard files |
| **Requirements** | `requirements.txt` | List of Python libraries needed to run the dashboard, installable via pip or in the Docker container. |
| **Bash Script** | `build.sh` | Bash script to automate the building and pushing of docker images to the ECS and Lambda |
| **Dockerfile** | `Dockerfile` | Docker script to build the image for creating the dashboard. |

## `Homepage.py` - Homepage of the dashboard

Queries the Glue DB via Athena to collect data for games that are currently discounted. This then formats the data into a page-based dataframe to display on the homepage, containing filters for games to include in the dataframe and ordering of it. Running this file will also run the other pages

### Features

- Glue DB connection via Athena
- Streamlit dataframe for discount data that is page-based
- Navigation buttons that take you to the other pages
- Streamlit filters

## `1_Game Tracker.py` - Game Tracker page of the dashboard

Queries the Glue DB to collect all of the data in the database. This is then transformed to show price history over time as a streamlit chart as a line graph with altair. This also contains the tracking system to send out email alerts as well as removing emails from the database, which connects to the RDS and adds to/deletes from it. This is found within the pages directory and runs by running Homepage.py, which is the syntax for creating pages on Streamlit. 

### Features
- Glue DB connection via Athena
- RDS connection via psycopg2
- Streamlit chart
- Streamlit filters
- Altair line chart

## `1_Login.py` - Login page of the dashboard

Requests user input with an email and password to create an account. This account allows for the storing of a wishlist that can be loaded upon login. The wishlist functionality has not been implemented yet, but this has been partly set up currently to show it can be done.

### Features

- Streamlit buttons to login
- Email validation (checking if the inputted email has the format of an email)

## `Backend.py` - Homepage of the dashboard

This file contains all of the backend functions required for all of the dashboard files. This contains all functions that are repeated between files, so that they can be changed in one place rather than in multiple. This includes connections for RDS and Glue, as well as email validation and async functions. 

### Features

- Boto3 client
- Psycopg2 connections
- Email validation
- Hiding password entry
