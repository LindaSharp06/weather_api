# Weather / Exchange Rate API Integration

This project retrieves exchange rates from a public API, processes the data, and stores it in a PostgreSQL database. It implements **Option A: Integration with an external API** and provides Docker Compose deployment.

---

## **Deploy with Docker Compose**

### 1. Clone and enter the project:

```bash
git clone <repository-url>
cd weather
```
---
### 2. Sample .env content:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=weather
DB_USER=postgres
DB_PASSWORD=twin123
```
---
### 3. Build and run with Docker Compose:
```bash
docker compose up -d --build
```
---

### 4. Run migrations (first time):
```bash
docker compose exec web python manage.py migrate
```
---
### 5. Access the API:
```bash

- Fetch exchange rate:
GET or POST → http://localhost:8000/api/get_exchange_rate/

- View stored history:
GET → http://localhost:8000/api/exchange_history/



| # | Requirement | Implementation |
|---|-------------|----------------|
| 1 | Python script that requests exchange rates (or weather) from a public API **every N minutes** | **`run_fetcher.py`** — runs in a loop, interval set by `FETCH_INTERVAL_MINUTES` (default 5). Uses [exchangerate-api.com](https://www.exchangerate-api.com/). Also: `python manage.py fetch_exchange_rate --loop --interval N`. |
| 2 | Store data in PostgreSQL with **at least two related tables** and a **foreign key** | **`requests`** (id, timestamp) and **`responses`** (id, **request_id** FK → requests.id, exchange_rate, status_code). Defined in `api_integration/exchange_rate.py`; created via `create_exchange_tables` or on first save. |
| 3 | **SQL query with JOIN** that exports request history and received data | **`sql/export_request_history.sql`** — JOIN of `requests` and `responses`. Same query in README below and used by `get_stored_history()` / `export_request_history()`. |
| 4 | **Logging of connection errors and timeouts** to a **separate file** | **`api_connection_errors.log`** (project root). Configured in `api_integration/exchange_rate.py`; logs `Timeout`, `ConnectionError`, and other `RequestException` with traceback. |

---


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
---
### To run this query against the Docker database:
```bash
docker compose exec -e PGPASSWORD=twin123 db psql -U postgres -d weather -f - < sql/export_request_history.sql
```
---
Alternatively, you can open a DB shell and paste the query:
```bash
docker compose exec -e PGPASSWORD=twin123 db psql -U postgres -d weather
```
---
## Requirements

Python 3.8+
PostgreSQL
Dependencies in requirements.txt (Django, requests, psycopg2-binary, SQLAlchemy, python-dotenv)
