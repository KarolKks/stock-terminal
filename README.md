# Stock Terminal

This project contains a FastAPI-based API and a PostgreSQL database, run with Docker Compose.
The desktop frontend is built with PySide6, Matplotlib, and Seaborn.

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
│   ├── tests/
│   │   ├── conftest.py            # Test fixtures and setup
│   │   ├── pytest.ini             # Pytest configuration
│   │   ├── test_auth.py           # Authentication endpoint tests
│   │   └── __init__.py
│   ├── Dockerfile                 # API container image
│   └── requirements.txt           # Python dependencies (backend)
├── frontend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py              # HTTP client for backend REST API communication
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── styles.py              # Colour palette and QSS stylesheets
│   │   ├── chart_widget.py        # Interactive Matplotlib/Seaborn stock chart widget
│   │   ├── login_form.py          # Login form widget (left panel)
│   │   ├── register_form.py       # Registration form widget (left panel)
│   │   └── login_window.py        # Main window combining form + chart panels
│   ├── main.py                    # Desktop application entry point
│   └── requirements.txt           # Python dependencies (frontend)
├── docker-compose.yml             # API and PostgreSQL service configuration
├── .env                           # Local environment configuration (create your own)
└── README.md
```

## Environment configuration

Create your own `.env` file in the project root. It is ignored by Git. Required variables are `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `SECRET_KEY`.

## Run backend with Docker

From the project root, run:

```bash
docker compose up --build
```

API documentation is available at `http://localhost:8000/docs`. To stop the services, run `docker compose down`.

## Run backend tests

```bash
docker compose exec api pytest -v
```

## Run frontend (desktop application)

1. Create a virtual environment and install dependencies:

```bash
cd frontend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS
pip install -r requirements.txt
```

2. Start the application:

```bash
python main.py
```

> **Note:** The backend must be running (`docker compose up`) for login and registration to work. The interactive chart works independently without a backend connection.

## Frontend features

- **Login form** – authenticate with username and password via the backend API (`POST /auth/login`)
- **Registration form** – create a new account (`POST /auth/register`) with client-side validation
- **Interactive stock chart** – fictional TechCorp (TCRP) stock price rendered with Matplotlib and Seaborn, with hover tooltips showing date, price, and volume
- **Password visibility toggle** – show/hide password in the login form
- **Form switching** – seamless navigation between login and registration views
