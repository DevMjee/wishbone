# Wishbone


## What is Wishbone?

Wishbone is a tool for comparing video-game prices across multiple online marketplaces, with a focus on helping users find the best deals.  

It aims to offer:
- Price data from various storefronts  
- Notifications, tracking for price drops and sales  

## Architecture & Components

The project is implemented in Python, with supporting terraform, scripts, Docker configs, and more. Key components include:

- `source/` — core application code, data-fetching, parsing, backend logic.  
- `database/` — storage backend, schema for tables on the RDS 
- `assets/`, `diagrams/` —  architecture diagrams, ERD logos.  
- `requirements.txt` — list of external dependencies / Python packages.  


## User Stories / Use Cases

Wishbone is designed with different types of users in mind. Some example scenarios:

- **Budget-conscious gamer**  
  > I want a way to easily compare the prices for any given game across multiple providers so I can get the game at the lowest price.  

- **Marketplace price-matching manager**  
  > I want to know about price trends in the market and sales occurring at any given time — to ensure our platform always offers better value.  




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




## Credits 
- Annie Bullough - Quality Assurance, Data Engineer & Analyst
- Adam Cummings - Architect, Data Engineer & Analyst
- Ronn Marakkalsherry - Business Analyst, Data Engineer & Analyst
- Dev Mukherjee - Project Manager, Data Engineer & Analyst
- Mahfuzur Rahman - Architect, Data Engineer & Analyst




