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
│   │   │   ├── user.py            # User database operations
│   │   │   └── watchlist.py       # Watchlist categories and items operations
│   │   ├── db/
│   │   │   └── database.py        # Database connection and SQLAlchemy sessions
│   │   ├── models/
│   │   │   ├── refresh_token.py   # Refresh-token database model
│   │   │   ├── user.py            # User database model
│   │   │   └── watchlist.py       # Watchlist categories and items models
│   │   ├── routers/
│   │   │   ├── auth.py            # Registration, login, and authentication endpoints
│   │   │   ├── market.py          # OHLCV candlestick market data endpoints
│   │   │   └── watchlist.py       # Watchlist categories and tickers management
│   │   ├── schemas/
│   │   │   ├── user.py            # Auth input and output schemas
│   │   │   ├── market.py          # Market data interval, period, and candle schemas
│   │   │   └── watchlist.py       # Watchlist category and ticker schemas
│   │   ├── services/
│   │   │   └── market_data.py     # Yahoo Finance data fetching and validation service
│   │   └── main.py                # FastAPI application and router registration
│   ├── tests/
│   │   ├── conftest.py            # Test fixtures and setup
│   │   ├── pytest.ini             # Pytest configuration
│   │   ├── test_auth.py           # Authentication endpoint tests
│   │   ├── test_market.py         # Market data endpoint tests
│   │   ├── test_watchlist.py      # Watchlist management tests
│   │   └── __init__.py
│   ├── Dockerfile                 # API container image
│   └── requirements.txt           # Python dependencies (backend)
├── frontend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py              # HTTP client for REST API communication (auth, watchlists, market)
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── styles.py              # Colour palette and QSS stylesheets (Navy / Inter styling)
│   │   ├── chart_widget.py        # Demo/login chart widget
│   │   ├── market_chart_widget.py # Interactive OHLCV market chart widget (Matplotlib + Seaborn)
│   │   ├── login_form.py          # Login form widget (left panel)
│   │   ├── register_form.py       # Registration form widget (left panel)
│   │   ├── login_window.py        # Login & registration window
│   │   └── terminal_window.py     # Main investor terminal dashboard (watchlists & market charts)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── worker.py              # Background thread runner for non-blocking API calls
│   ├── assets/
│   │   └── fonts/
│   │       └── Inter-Variable.ttf # Custom typography (Inter font)
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

## Frontend features

- **Ekran logowania i rejestracji** (`LoginWindow`):
  - Uwierzytelnianie użytkownika (`POST /auth/login`) i rejestracja (`POST /auth/register`).
  - Elegancka czcionka **Inter** i stylistyka w kolorach Navy (`#2B2D6E`) oraz Primary Blue (`#3F51B5`).
  - Podgląd hasła, przełączanie formularzy oraz demonstracyjny wykres.
- **Pulpit inwestora po zalogowaniu** (`TerminalWindow`):
  - **Zarządzanie watchlistami**:
    - Tworzenie nowej kategorii (`POST /watchlists/categories`).
    - Zmiana nazwy kategorii (`PATCH /watchlists/categories/{id}`).
    - Usuwanie kategorii (`DELETE /watchlists/categories/{id}`).
    - Dodawanie tickerów z weryfikacją giełdową (`POST /watchlists/categories/{id}/items`).
    - Usuwanie tickerów z kategorii (`DELETE /watchlists/categories/{id}/items/{ticker}`).
  - **Interaktywny wykres notowań rynkowych** (`MarketChartWidget`):
    - Pobieranie danych historycznych OHLCV (`GET /market/candles/{ticker}`).
    - Wybór instrumentu z rozwijanej listy (`QComboBox`) lub bezpośrednio z listy watchlisty.
    - Konfiguracja okresu (`1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `ytd`, `max`).
    - Konfiguracja interwału (`1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1wk`, `1mo`).
    - Płynny blitting 60fps przy najeżdżaniu myszką.
    - Celownik (crosshair) oraz dymek informacyjny z datą, kursem zamknięcia, otwarcia, min/max oraz wolumenem.
    - Dymek automatycznie przeskakuje na lewą stronę po przekroczeniu połowy wykresu, zapobiegając ucinaniu treści.
  - **Wielowątkowość w Qt**:
    - Zapytania sieciowe są asynchronicznie delegowane do puli wątków (`QThreadPool`), dzięki czemu interfejs pozostaje w 100% płynny podczas ładowania danych giełdowych.
