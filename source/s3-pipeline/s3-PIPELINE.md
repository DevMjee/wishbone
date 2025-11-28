## Overview

| Component | File | Description |
|-----------|------|-------------|
| **Historical Pipeline** | `historical_pipeline.py` | Short description of the script |
|**Test Historical Pipeline**|`test_historical_pipeline.py`| Short description of the script (repeat as necessary)|
| **Dockerfile** | `Dockerfile` | Docker script to build the pipeline|
| **Requirements** | `requirements.txt` | List of Python libraries needed to run the pipeline installable via pip or in the Docker container. |
| **Bash Script** | `build.sh` | Bash script to automate the building and pushing of docker images to the ECS and Lambda | 
---

## `historical_pipeline.py` — Historical Pipeline

### What It Does
The `historical_pipeline.py` script removes old data from the RDS and transfers any to the S3 bucket

Features of the script
- List script features/functionality for script
- 
- 


Repeat this for as many .py scripts listed up above

## `test_historical_pipeline.py` — Historical Pipeline

### What It Does
The `test_historical_pipeline.py` script removes old data from the RDS and transfers any to the S3 bucket

Features of the script
- List script features/functionality for script
- 
- 


Repeat this for as many .py scripts listed up above



---

### Configuration

The script requires the following environment variables, either loaded locally via a `.env` file, or through AWS secrets manager:  

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

