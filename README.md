# Weather / Exchange Rate API Integration

Service that retrieves exchange rates from a public API, processes the data, and saves it to PostgreSQL. Implements **Option A: Integration with an external API**.

---

## How to submit

**Submit a link to the repository.**

This README includes what is required for submission:

1. **Deploy with Docker Compose (with database)** — see section [Deploy with Docker Compose](#deploy-with-docker-compose) below.
2. **Sample .env file** — the project includes **`.env.example`** (copy to `.env` and adjust). Its contents are also shown in the README under [Environment file](#2-environment-file).
3. **SQL query with JOIN** — see section [SQL query: export request history (JOIN)](#sql-query-export-request-history-join) below.

---

## Task requirements (checklist)

| # | Requirement | Implementation |
|---|-------------|----------------|
| 1 | Python script that requests exchange rates (or weather) from a public API **every N minutes** | **`run_fetcher.py`** — runs in a loop, interval set by `FETCH_INTERVAL_MINUTES` (default 5). Uses [exchangerate-api.com](https://www.exchangerate-api.com/). Also: `python manage.py fetch_exchange_rate --loop --interval N`. |
| 2 | Store data in PostgreSQL with **at least two related tables** and a **foreign key** | **`requests`** (id, timestamp) and **`responses`** (id, **request_id** FK → requests.id, exchange_rate, status_code). Defined in `api_integration/exchange_rate.py`; created via `create_exchange_tables` or on first save. |
| 3 | **SQL query with JOIN** that exports request history and received data | **`sql/export_request_history.sql`** — JOIN of `requests` and `responses`. Same query in README below and used by `get_stored_history()` / `export_request_history()`. |
| 4 | **Logging of connection errors and timeouts** to a **separate file** | **`api_connection_errors.log`** (project root). Configured in `api_integration/exchange_rate.py`; logs `Timeout`, `ConnectionError`, and other `RequestException` with traceback. |

---

## Features

- **External API**: Fetches exchange rates from [exchangerate-api.com](https://www.exchangerate-api.com/) (latest USD rates).
- **PostgreSQL storage**: Two related tables — `requests` (request timestamp) and `responses` (exchange rate, status) — with a foreign key from `responses.request_id` to `requests.id`.
- **Scheduled fetch**: Python script and Django management command to fetch every **N minutes** (configurable).
- **SQL JOIN**: Query to export request history with received data (see below).
- **Logging**: Connection errors and timeouts are logged to a separate file: `api_connection_errors.log`.

---

## Deploy with Docker Compose

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd weather
```

### 2. Environment file (sample .env)

A **sample `.env` file** is provided as **`.env.example`**. Copy it to `.env` and adjust if needed:

```bash
cp .env.example .env
```

For Docker you can keep defaults; the Compose file sets `DB_HOST=db`, `DB_PASSWORD=twin123`, etc., for the app container.

**Contents of `.env.example` (sample for local runs; Docker overrides with its own env):**

```env
# PostgreSQL (required for storing exchange rate data)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=weather
DB_USER=postgres
DB_PASSWORD=twin123

# Optional
# DATABASE_URL=postgres://postgres:twin123@localhost:5432/weather
# FETCH_INTERVAL_MINUTES=5
# FETCH_INTERVAL_SECONDS=30
# API_TIMEOUT=10
```

### 3. Build and run

```bash
docker compose up -d --build
```

This starts:

- **PostgreSQL** (port 5432, database `weather`, user `postgres`, password `twin123`)
- **Django app** (port 8000), waiting for the DB to be ready

### 4. Run migrations (first time)

```bash
docker compose exec web python manage.py migrate
```

### 5. Use the API

- **Fetch and store exchange rate**:  
  `GET` or `POST` → `http://localhost:8000/api/get_exchange_rate/`
- **View stored history**:  
  `GET` → `http://localhost:8000/api/exchange_history/`

---

## Fetch every N minutes

### Option 1: Standalone script

From the project root (with `.env` and DB configured):

```bash
# Default: every 5 minutes
python run_fetcher.py
```

Set interval (minutes) via env:

```bash
# Windows (PowerShell)
$env:FETCH_INTERVAL_MINUTES=10
python run_fetcher.py

# Linux/macOS
export FETCH_INTERVAL_MINUTES=10
python run_fetcher.py
```

Or add `FETCH_INTERVAL_MINUTES=10` to `.env`.

### Option 2: Django management command (one-shot or loop)

One-shot (fetch once):

```bash
python manage.py fetch_exchange_rate
```

Loop every N minutes (e.g. 5):

```bash
python manage.py fetch_exchange_rate --loop --interval 5
```

With Docker:

```bash
docker compose exec web python manage.py fetch_exchange_rate --loop --interval 5
```

---

## Database schema

- **`requests`**: `id` (PK), `timestamp`
- **`responses`**: `id` (PK), `request_id` (FK → `requests.id`), `exchange_rate`, `status_code`

Tables are created automatically by the app (SQLAlchemy) on first use.

---

## SQL query: export request history (JOIN)

This query exports the request history and the received data by joining `requests` and `responses`:

```sql
SELECT
    r.id          AS request_id,
    r.timestamp   AS request_time,
    res.id        AS response_id,
    res.exchange_rate,
    res.status_code
FROM requests r
JOIN responses res ON res.request_id = r.id
ORDER BY r.id DESC;
```

The same query is in `sql/export_request_history.sql`. To run it against the Docker database:

```bash
docker compose exec -e PGPASSWORD=twin123 db psql -U postgres -d weather -f - < sql/export_request_history.sql
```

Or open a DB shell and paste the query:

```bash
docker compose exec -e PGPASSWORD=twin123 db psql -U postgres -d weather
```

---

## Logging

- **Connection errors and timeouts** (API requests) are logged to:
  - **`api_connection_errors.log`** (in the project root)

Errors logged include:

- Connection errors
- Timeouts
- Other request-related exceptions (with traceback)

---

## Local development (without Docker)

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and set your PostgreSQL credentials.
3. Ensure PostgreSQL is running and database `weather` exists (or create it).
4. Run migrations: `python manage.py migrate`
5. Start the server: `python manage.py runserver`
6. Optional: run the fetcher script in another terminal: `python run_fetcher.py`

---

## Requirements

- Python 3.8+
- PostgreSQL
- See `requirements.txt` (Django, requests, psycopg2-binary, SQLAlchemy, python-dotenv)
