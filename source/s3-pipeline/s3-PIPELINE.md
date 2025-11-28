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
The `historical_pipeline.py` script removes old data from the RDS and transfers any to the S3 bucket. Data is converted to time partitioned parquet files

Features of the script
- Connects to the RDS and S3 bucket
- Creates parquet files
- Clears old data from the RDS



## `test_historical_pipeline.py` — Historical Pipeline

### What It Does
The `test_historical_pipeline.py` script tests the functionality of the historical pipeline script

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

