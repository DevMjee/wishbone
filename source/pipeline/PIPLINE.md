## Overview

| Component | File | Description |
|-----------|------|-------------|
| **Script name** | `file_name.py` | Short description of the script |
|**Second Script name**|`second_file_name.py`| Short description of the script (repeat as necessary)|
| **Dockerfile** | `Dockerfile` | Docker script to build ... |
| **Requirements** | `requirements.txt` | List of Python libraries needed to run the ..., installable via pip or in the Docker container. |
| **Bash Script** | `build.sh` | Bash script to automate the building and pushing of docker images to the ECS and Lambda | 
---

## `file_name.py` — Script name

### What It Does
The `file.py` script ... (2-3 sentences here on what the script does)

Features of the script
- List script features/functionality for script
- 
- 


Repeat this for as many .py scripts listed up above



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

