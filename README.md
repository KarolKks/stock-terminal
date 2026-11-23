# Stock Terminal

Stock Terminal is a desktop stock-market application built with a FastAPI backend,
PostgreSQL, Docker Compose, and a PySide6/Matplotlib frontend.

The current implementation includes user registration and authentication, refresh
tokens, authenticated watchlist categories and tickers, historical OHLCV candlestick
data, fundamentals data, and a complete investor terminal interface.

## MVP data-provider notice

> **Development and testing only:** the current market and fundamental-data
> integration uses `yfinance` exclusively for MVP development and testing.
>
> `yfinance` is not suitable as the sole production provider for an application
> with many concurrent users. It has no official service-level agreement (SLA),
> applies aggressive upstream request throttling, and can cause the server IP to
> be blocked when requests are sent in parallel or in large volumes. Its calls are
> synchronous, so the backend must offload them to background threads. For GPW
> (Warsaw Stock Exchange) companies, quote data can be delayed by approximately
> 15 minutes. Production use should rely on an authenticated, licensed market-data
> provider with rate limiting, caching, an explicit SLA, and appropriate GPW data
> coverage.

## Current modules

### Backend

- **Auth**: registration, login, current-user lookup, refresh-token handling, and logout.
- **Watchlists**: user-owned categories and ticker items.
- **Market data**: authenticated historical OHLCV candles from `yfinance`.
- **Fundamentals**: company profile and valuation metrics, annual or quarterly
  income/balance/cash-flow statements, and annual dividend history from `yfinance`.

The fundamentals API is exposed as:

- `GET /market/fundamentals/{ticker}/overview`
- `GET /market/fundamentals/{ticker}/financials?period=annual|quarterly`
- `GET /market/fundamentals/{ticker}/dividends`

All fundamentals endpoints require `Authorization: Bearer <access_token>`.

### Frontend

- **Login and registration**: authentication, registration, password visibility,
  Inter typography, and the styled Navy/Primary Blue interface.
- **Investor terminal**: watchlist management and interactive market charts.
- **Watchlists**: create, rename, and delete categories; add and remove tickers.
- **Market charts**: OHLCV data, period and interval controls, hover crosshair,
  and automatic tooltip positioning.
- **Asynchronous networking**: API requests run in background worker threads to
  keep the Qt interface responsive.

## Project structure

```text
.
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   ├── crud/
│   │   │   ├── refresh_token.py
│   │   │   ├── user.py
│   │   │   └── watchlist.py
│   │   ├── db/
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── refresh_token.py
│   │   │   ├── user.py
│   │   │   └── watchlist.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── fundamentals.py
│   │   │   ├── market.py
│   │   │   └── watchlist.py
│   │   ├── schemas/
│   │   │   ├── fundamentals.py
│   │   │   ├── market.py
│   │   │   ├── user.py
│   │   │   └── watchlist.py
│   │   ├── services/
│   │   │   ├── fundamentals.py
│   │   │   └── market_data.py
│   │   └── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── pytest.ini
│   │   ├── test_auth.py
│   │   ├── test_market.py
│   │   └── test_watchlist.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── chart_widget.py
│   │   ├── market_chart_widget.py
│   │   ├── login_form.py
│   │   ├── login_window.py
│   │   ├── register_form.py
│   │   ├── styles.py
│   │   └── terminal_window.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── worker.py
│   ├── assets/
│   │   └── fonts/
│   │       └── Inter-Variable.ttf
│   ├── main.py
│   └── requirements.txt
├── docs/
│   └── PROJECT_GUIDE.md
├── docker-compose.yml
├── .env
└── README.md
```

## Environment configuration

Create a `.env` file in the project root. It is ignored by Git. Required variables are
`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `SECRET_KEY`.

## Run the backend with Docker

From the project root, run:

```bash
docker compose up --build
```

API documentation is available at `http://localhost:8000/docs`. Stop the services
with `docker compose down`.

## Run backend tests

```bash
docker compose exec api pytest -v
```

## Run the frontend

1. Create a virtual environment and install dependencies:

```bash
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Start the application:

```bash
python main.py
```

> **Note:** the backend must be running with `docker compose up` for authentication,
> watchlist, market, and fundamental API features.
