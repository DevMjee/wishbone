## Overview

| Component | File | Description |
|-----------|------|-------------|
| **extract** | `extract.py` | Web scrapes from game platforms via their search web address (GOG and Steam) |
|**transform**|`transform.py`| Configures data into dictionaries prepared for RDS |
|**load**|`load.py`| Connects and loads data into RDS |
| **etl_Dockerfile** | `Dockerfile` | Docker script to build daily pipeline |
| **search_Dockerfile** | `Dockerfile` | Docker script to build search function backend|
| **Requirements** | `requirements.txt` | List of Python libraries needed to run the ..., installable via pip or in the Docker container. |
| **ETL Bash Script** | `etl_build.sh` | Bash script to automate the building and pushing of docker images to the ECS and Lambda for the ETL | 
| **Search Bash Script** | `search_build.sh` | Bash script to automate the building and pushing of docker images to the ECS and Lambda for the search function| 
---

## `extract.py`

### What It Does
The `extract.py` script web scrapes from web addresses based on search results pages for both Steam and GOG. This script grabs the price of the first result only.

Features of the script
- Steam Path: 'https://store.steampowered.com/search?term={search_term}'
- GOG Path: 'https://catalog.gog.com/v1/catalog?limit=48&query=like%3A{search_term}' 
- Uses a list of strings

The `transform.py` script loads the results of the extract (saved as separate json) into one combined cleaned json file.

Features of the script
- exports 'clean_data.json' 

The `load.py` script pushes data to the RDS.

Features of the script
- Mainly loads to listings tables 




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

