import sqlite3
from database.db import get_db_connection


def validate_student(name, roll_no):
    name, roll = (name or "").strip(), (roll_no or "").strip()
    if not name or len(name) > 100 or any(ord(c) < 32 for c in name):
        raise ValueError("Enter a valid student name (1–100 characters).")
    if not roll or len(roll) > 40 or any(ord(c) < 33 for c in roll):
        raise ValueError("Enter a valid roll number (1–40 characters, no spaces).")
    return name, roll


def register_student(event_id, student_name, roll_no):
    name, roll = validate_student(student_name, roll_no)
    conn = get_db_connection()
    conn.execute("BEGIN IMMEDIATE")
    try:
        if conn.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone() is None:
            raise LookupError("Event not found.")
        if conn.execute("SELECT 1 FROM registrations WHERE event_id=? AND roll_no=?", (event_id,roll)).fetchone():
            raise ValueError("This roll number already has a registration for this event.")
        cur = conn.execute("UPDATE events SET registered=registered+1 WHERE event_id=? AND registered<seats", (event_id,))
        if cur.rowcount != 1:
            raise ValueError("This event is full.")
        cur = conn.execute("INSERT INTO registrations(event_id,student_name,roll_no) VALUES(?,?,?)", (event_id,name,roll))
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise


def cancel_registration(reg_id, roll_no=None):
    conn = get_db_connection()
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute("SELECT event_id,roll_no,status FROM registrations WHERE reg_id=?", (reg_id,)).fetchone()
        if row is None or (roll_no is not None and row["roll_no"] != roll_no.strip()):
            raise LookupError("Registration not found.")
        if row["status"] != "ACTIVE":
            raise ValueError("This registration has already been cancelled.")
        cur = conn.execute("UPDATE registrations SET status='CANCELLED' WHERE reg_id=? AND status='ACTIVE'", (reg_id,))
        if cur.rowcount != 1:
            raise ValueError("This registration has already been cancelled.")
        cur = conn.execute("UPDATE events SET registered=registered-1 WHERE event_id=? AND registered>0", (row["event_id"],))
        if cur.rowcount != 1:
            raise RuntimeError("Event seat count is inconsistent.")
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def registrations_for_roll(roll):
    return get_db_connection().execute("SELECT r.*,e.name AS event_name,e.event_date FROM registrations r JOIN events e USING(event_id) WHERE r.roll_no=? ORDER BY r.registered_at DESC", (roll,)).fetchall()
