from datetime import date
from database.db import get_db_connection


def validate_event(name, event_date, seats):
    name = (name or "").strip()
    if not name or len(name) > 120:
        raise ValueError("Event name is required and must be at most 120 characters.")
    try:
        parsed = date.fromisoformat((event_date or "").strip())
    except ValueError:
        raise ValueError("Enter a valid event date.")
    try:
        seats = int(seats)
    except (TypeError, ValueError):
        raise ValueError("Seat capacity must be a positive whole number.")
    if seats <= 0:
        raise ValueError("Seat capacity must be a positive whole number.")
    return name, parsed.isoformat(), seats


def create_event(name, event_date, seats):
    name, event_date, seats = validate_event(name, event_date, seats)
    cur = get_db_connection().execute("INSERT INTO events(name,event_date,seats) VALUES(?,?,?)", (name, event_date, seats))
    return cur.lastrowid


def update_event(event_id, name, event_date, seats):
    name, event_date, seats = validate_event(name, event_date, seats)
    conn = get_db_connection()
    row = conn.execute("SELECT registered FROM events WHERE event_id=?", (event_id,)).fetchone()
    if row is None:
        raise LookupError("Event not found.")
    if seats < row["registered"]:
        raise ValueError("Capacity cannot be lower than active registrations.")
    conn.execute("UPDATE events SET name=?,event_date=?,seats=? WHERE event_id=?", (name,event_date,seats,event_id))


def delete_event(event_id):
    conn = get_db_connection()
    row = conn.execute("SELECT COUNT(*) AS n FROM registrations WHERE event_id=?", (event_id,)).fetchone()
    if conn.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone() is None:
        raise LookupError("Event not found.")
    if row["n"]:
        raise ValueError("This event has registration records and cannot be deleted.")
    conn.execute("DELETE FROM events WHERE event_id=?", (event_id,))


def list_events():
    return get_db_connection().execute("SELECT *, seats-registered AS available FROM events ORDER BY event_date,event_id").fetchall()


def get_event(event_id):
    return get_db_connection().execute("SELECT *, seats-registered AS available FROM events WHERE event_id=?", (event_id,)).fetchone()
