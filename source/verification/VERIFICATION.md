## Overview

| Component | File | Description |
|-----------|------|-------------|
| **Email Verification** | `verification.py` | Checks the emails stored on the RDS and removes unverified emails |
| **Dockerfile** | `Dockerfile` | Docker script to build the lambda function |
| **Requirements** | `requirements.txt` | List of Python libraries needed to run the script installable via pip or in the Docker container. |
| **Bash Script** | `build.sh` | Bash script to automate the building and pushing of docker images to the ECS and Lambda | 
---

## `verification.py` — Script name

### What It Does
The `verification.py` script collects the the emails registered on the database and checks if they have been verified on AWS. Emails that are unverified are removed from the database. 

Features of the script
- Connects to RDS database 
- Uses Boto3 to connect to the SES and list verified emails
- Removes emails that are unverified from the database


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

---

