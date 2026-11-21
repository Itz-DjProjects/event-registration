import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "instance" / "events.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def connect_db(path=None):
    db_path = path or DATABASE_PATH
    if str(db_path) != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def get_db_connection():
    from flask import current_app, g
    if "db" not in g:
        g.db = connect_db(current_app.config["DATABASE"])
    return g.db


def close_db(_error=None):
    from flask import g
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def initialize_database(path=None):
    conn = connect_db(path)
    try:
        conn.executescript(SCHEMA_PATH.read_text())
    finally:
        conn.close()


def get_tables(path=None):
    conn = connect_db(path)
    try:
        return [r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    finally:
        conn.close()


def database_status():
    return DATABASE_PATH.exists()
