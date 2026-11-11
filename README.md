# Stock Terminal

This project contains a FastAPI-based API and a PostgreSQL database, run with Docker Compose.

## Struktura projektu

```text
.
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Application settings and database connection configuration
│   │   │   ├── dependencies.py    # API dependencies, including user authentication
│   │   │   └── security.py        # Password and token handling
│   │   ├── crud/
│   │   │   ├── refresh_token.py   # Refresh-token database operations
│   │   │   └── user.py            # User database operations
│   │   ├── db/
│   │   │   └── database.py        # Database connection and SQLAlchemy sessions
│   │   ├── models/
│   │   │   ├── refresh_token.py   # Refresh-token database model
│   │   │   └── user.py            # User database model
│   │   ├── routers/
│   │   │   └── auth.py            # Registration, login, and authentication endpoints
│   │   ├── schemas/
│   │   │   └── user.py            # API input and output data schemas
│   │   └── main.py                # FastAPI application and router registration
│   ├── Dockerfile                 # API container image
│   └── requirements.txt           # Python dependencies
├── docker-compose.yml             # API and PostgreSQL service configuration
└── .env                           # Local environment configuration (create your own)
```

## Environment configuration

Create your own `.env` file in the project root. It is ignored by Git. Required variables are `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `SECRET_KEY`. Do not share or commit passwords or secret keys.

## Run with Docker

From the project root, run:

```bash
docker compose up --build
```

This builds the API image and starts the API and database. API documentation is available at `http://localhost:8000/docs`. To stop the services, run `docker compose down`.
