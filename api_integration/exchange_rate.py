import os
import logging
import time
from pathlib import Path
from datetime import datetime

import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Load .env (override=False so Docker env is not overwritten)
_root = Path(__file__).resolve().parent.parent
if (_root / ".env").exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_root / ".env", override=False)
    except ImportError:
        pass

logger = logging.getLogger(__name__)
_handler = logging.FileHandler(_root / "api_connection_errors.log", encoding="utf-8")
_handler.setLevel(logging.ERROR)
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
logger.addHandler(_handler)

# Tables: requests, responses (FK request_id -> requests.id)
Base = declarative_base()

class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    timestamp = Column(String, nullable=False)

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('requests.id'), nullable=False)
    exchange_rate = Column(Float)
    status_code = Column(Integer)

    request = relationship("Request", back_populates="responses")

Request.responses = relationship("Response", order_by=Response.id, back_populates="request")

_engine = None
_session = None

def _get_engine():
    global _engine
    if _engine is None:
        url = os.environ.get("DATABASE_URL")
        if url:
            if url.startswith("postgres://"):
                url = "postgresql://" + url[11:]
            elif not url.startswith("postgresql://"):
                url = "postgresql://" + url
        else:
            url = "postgresql://{user}:{pw}@{host}:{port}/{db}".format(
                user=os.environ.get("DB_USER", "postgres"),
                pw=os.environ.get("DB_PASSWORD", "twin123"),
                host=os.environ.get("DB_HOST", "localhost"),
                port=os.environ.get("DB_PORT", "5432"),
                db=os.environ.get("DB_NAME", "weather"),
            )
        _engine = create_engine(url)
        Base.metadata.create_all(_engine)
    return _engine

def _get_session():
    global _session
    if _session is None:
        _session = sessionmaker(bind=_get_engine())()
    return _session

def get_exchange_rate():
    """Fetch exchange rate from API. Logs errors/timeouts to api_connection_errors.log."""
    url = "https://v6.exchangerate-api.com/v6/c172530ea7d0b2965295449e/latest/USD"
    timeout_seconds = int(os.environ.get("API_TIMEOUT", "10"))
    try:
        response = requests.get(url, timeout=timeout_seconds)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout as e:
        logger.error("API timeout fetching exchange rate: %s (timeout=%ss)", e, timeout_seconds, exc_info=True)
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error("API connection error fetching exchange rate: %s", e, exc_info=True)
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching exchange rate: %s", e, exc_info=True)
        return None

def save_to_db(data):
    """Save data to PostgreSQL database"""
    session = _get_session()
    try:
        request = Request(timestamp=str(datetime.now()))
        session.add(request)
        session.commit()

        response = Response(
            request_id=request.id,
            exchange_rate=data['conversion_rates']['EUR'],
            status_code=200
        )
        session.add(response)
        session.commit()

    except Exception as e:
        logger.error("Error saving data to database: %s", e, exc_info=True)
        session.rollback()

def fetch_and_store_data():
    """Fetch from API and store in the database."""
    data = get_exchange_rate()
    if data:
        save_to_db(data)

def get_stored_history(limit=50):
    """Return request history (JOIN) as list of dicts."""
    session = _get_session()
    result = session.execute(text("""
        SELECT r.id, r.timestamp, res.exchange_rate, res.status_code
        FROM requests r JOIN responses res ON res.request_id = r.id
        ORDER BY r.id DESC LIMIT :limit
    """), {"limit": limit})
    return [{"id": r[0], "timestamp": str(r[1]), "exchange_rate": r[2], "status_code": r[3]} for r in result]

def export_request_history():
    """Print request history (JOIN) to stdout."""
    session = _get_session()
    for row in session.execute(text("""
        SELECT r.id, r.timestamp, res.exchange_rate, res.status_code
        FROM requests r JOIN responses res ON res.request_id = r.id ORDER BY r.id DESC
    """)):
        print(row)

def _run_fetcher_loop(interval_minutes=5, interval_seconds=None):
    """Run fetch every N minutes or N seconds until interrupted."""
    sec = interval_seconds if interval_seconds is not None else 60 * interval_minutes
    sec = max(10, sec)
    while True:
        fetch_and_store_data()
        time.sleep(sec)

if __name__ == "__main__":
    try:
        s = os.environ.get("FETCH_INTERVAL_SECONDS")
        if s:
            n = max(10, min(int(s), 86400))
            print("Fetching every %s second(s). Ctrl+C to stop." % n)
            _run_fetcher_loop(interval_seconds=n)
        else:
            n = max(1, min(int(os.environ.get("FETCH_INTERVAL_MINUTES", "5")), 1440))
            print("Fetching every %s minute(s). Ctrl+C to stop." % n)
            _run_fetcher_loop(interval_minutes=n)
    except KeyboardInterrupt:
        print("Stopped.")