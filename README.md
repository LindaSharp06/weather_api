# Exchange Rate API Integration

Retrieves exchange rates from a public API, stores them in PostgreSQL, and exposes an API and dashboard. Implements **Option A: Integration with an external API**.

---

## Deploy with Docker Compose

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd weather
```

### 2. Sample `.env` file

Copy `.env.example` to `.env` and adjust if needed. Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=weather
DB_USER=postgres
DB_PASSWORD=twin123
```

For Docker, the Compose file sets `DB_HOST=db` and other variables for the web service.

### 3. Build and run

```bash
docker compose up -d --build
```

### 4. Create the database (if needed)

If you see **"database \"weather\" does not exist"** when running migrate, create the database:

```bash
docker compose exec db psql -U postgres -c "CREATE DATABASE weather;"
```

Then run migrations (step 5).

### 5. Run migrations (first time)

```bash
docker compose exec web python manage.py migrate
```

### 6. Use the API

- **Fetch and store exchange rate:** `GET` or `POST` → `http://localhost:8000/api/get_exchange_rate/`
- **View stored history:** `GET` → `http://localhost:8000/api/exchange_history/`
- **Dashboard (UI):** `http://localhost:8000/api/`

---

## Task requirements

| # | Requirement | Implementation |
|---|-------------|----------------|
| 1 | Python script that requests exchange rates every **N minutes** | `run_fetcher.py` (interval: `FETCH_INTERVAL_MINUTES` or `FETCH_INTERVAL_SECONDS` in `.env`). Or: `python manage.py fetch_exchange_rate --loop --interval N`. API: [exchangerate-api.com](https://www.exchangerate-api.com/). |
| 2 | Store in PostgreSQL with **two related tables** and a **foreign key** | Tables `requests` (id, timestamp) and `responses` (id, request_id → requests.id, exchange_rate, status_code). See `api_integration/exchange_rate.py`. |
| 3 | **SQL query with JOIN** to export request history and received data | `sql/export_request_history.sql` and the query below. |
| 4 | **Logging** of connection errors and timeouts to a **separate file** | `api_connection_errors.log` in the project root (see `api_integration/exchange_rate.py`). |

---

## SQL query (JOIN)

Export request history and received data:

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

**Run against the Docker database:**

- **Option A (any OS):** Open a psql shell, then paste the query above:
  ```bash
  docker compose exec -e PGPASSWORD=twin123 db psql -U postgres -d weather
  ```

- **Linux / macOS / Git Bash:** Run the SQL file:
  ```bash
  docker compose exec -e PGPASSWORD=twin123 db psql -U postgres -d weather -f - < sql/export_request_history.sql
  ```

- **PowerShell (Windows):** The `<` redirection does not work. Use the shell (Option A) or pipe the file:
  ```powershell
  Get-Content sql/export_request_history.sql | docker compose exec -T -e PGPASSWORD=twin123 db psql -U postgres -d weather
  ```

---

## Requirements

- Python 3.8+
- PostgreSQL
- See `requirements.txt`: Django, requests, psycopg2-binary, SQLAlchemy, python-dotenv
