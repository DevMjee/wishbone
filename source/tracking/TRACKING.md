## Overview

| Component | File | Description |
|-----------|------|-------------|
| **Email subscription management** | `tracking.py` | Lambda handler that adds and removes emails from the database |
| **Dockerfile** | `Dockerfile` | Docker script to build the lambda handler |
| **Requirements** | `requirements.txt` | List of Python libraries needed to run the lambda installable via pip or in the Docker container. |
| **Bash Script** | `build.sh` | Bash script to automate the building and pushing of docker images to the ECS and Lambda | 
---

## `tracking.py` — Email Subscription Management

### What It Does
The `tracking.py` script adds or removes emails from the tracking table of the RDS. Emails that are input are checked for AWS SES validation, with validation emails sent to not yet validated emails.

Features of the script
- Connects to the RDS Postgres database
- If a user choses to subscribe their email along with the game id is insert to the table
- If a user unsubscribes all instances of their email are removed 
- Uses Boto3 to send verification emails through SES to unverified emails 

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

---

