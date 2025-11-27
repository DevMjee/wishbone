## Overview

| Component | File | Description |
|-----------|------|-------------|
| **Email Alert Lambda** | `mailing.py` | Lambda handler to send out emails for tracked games if they reduce in price. |
|**Email Body Template**|`html_email.py`|Function to add personalised details to the HTML body of the alert email.  |
| **Dockerfile** | `Dockerfile` | Docker script to build the image for creating the lambda. |
| **Requirements** | `requirements.txt` | List of Python libraries needed to run the lambda, installable via pip or in the Docker container. |
| **Bash Script** | `build.sh` | Bash script to automate the building and pushing of docker images to the ECS and Lambda | 
---

## `mailing.py` — Email Alert Lambda

### What It Does
The `mailing.py` script connects to an RDS Postgres SQL Server and AWS Athena to retrieve game data. It determines if a game has reduced in price and then using AWS SES sends out email alerts to users tracking that game.

Features of the script
- RDS and Athena connections.
- Uses of Boto3 to connect to AWS SES to send emails.
- Identify games that have reduced in price and the emails for users tracking these games.
- Formatting of game prices from pennies to pounds, including the £ symbol 


## `email_html.py` — Email Body Formatting

### What It Does
The `email_html.py` script contains the HTML body of the email in a function allowing the insertion of relevant information. The email contains the full wishbone logo as a header and the wishbone logo footer. The following specific game information is added:

- Game name
- Current game price
- Previous game price


---

### Configuration

The script requires the following environment variables, loaded locally via a `.env` file:  

| Variable | Description |
|----------|-------------|
| `RDS_HOST` | RDS database host |
| `RDS_USER` | Database username |
| `RDS_PASSWORD` | Database password |
| `DB_NAME` | Database name |
| `PORT` | RDS access |
| `ACCESS_KEY_ID` | AWS access key for Athena queries |
| `AWS_SECRET_ACCESS_KEY_ID` | AWS secret key for Athena queries |
| `SENDER_EMAIL` | Email for sending alert emails from |

---

