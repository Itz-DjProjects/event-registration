from functools import wraps
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from database.db import get_db_connection
from services.event_service import create_event, delete_event, get_event, list_events, update_event

manager_bp = Blueprint("manager", __name__)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("manager_id"):
            flash("Please log in to access manager tools.", "error")
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

@manager_bp.get("/")
@login_required
def dashboard():
    conn = get_db_connection()
    events = list_events()
    stats = conn.execute("SELECT COUNT(*) AS events,COALESCE(SUM(registered),0) AS registrations,COALESCE(SUM(seats-registered),0) AS available FROM events").fetchone()
    return render_template("manager_dashboard.html", events=events, stats=stats)

@manager_bp.route("/events/add", methods=["GET", "POST"])
@login_required
def add_event():
    if request.method == "POST":
        try:
            create_event(request.form.get("name"), request.form.get("event_date"), request.form.get("seats"))
            flash("Event added successfully.", "success")
            return redirect(url_for("manager.dashboard"))
        except ValueError as exc: flash(str(exc), "error")
    return render_template("add_event.html")

@manager_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event = get_event(event_id)
    if event is None: abort(404)
    if request.method == "POST":
        try:
            update_event(event_id, request.form.get("name"), request.form.get("event_date"), request.form.get("seats"))
            flash("Event updated successfully.", "success")
            return redirect(url_for("manager.dashboard"))
        except ValueError as exc: flash(str(exc), "error")
    return render_template("edit_event.html", event=event)

@manager_bp.post("/events/<int:event_id>/delete")
@login_required
def remove_event(event_id):
    try:
        delete_event(event_id)
        flash("Event deleted.", "success")
    except (ValueError, LookupError) as exc: flash(str(exc), "error")
    return redirect(url_for("manager.dashboard"))

@manager_bp.get("/events/<int:event_id>/participants")
@login_required
def participants(event_id):
    event = get_event(event_id)
    if event is None: abort(404)
    rows = get_db_connection().execute("SELECT reg_id,student_name,roll_no,registered_at,status FROM registrations WHERE event_id=? ORDER BY registered_at DESC", (event_id,)).fetchall()
    return render_template("participants.html", event=event, participants=rows)

@manager_bp.get("/registrations")
@login_required
def all_registrations():
    rows = get_db_connection().execute("SELECT r.*,e.name AS event_name FROM registrations r JOIN events e USING(event_id) ORDER BY r.registered_at DESC").fetchall()
    return render_template("participants.html", event=None, participants=rows)

@manager_bp.get("/summary")
@login_required
def summary():
    rows = get_db_connection().execute("SELECT e.event_id,e.name,e.seats,COUNT(CASE WHEN r.status='ACTIVE' THEN r.reg_id END) AS active, e.seats-COUNT(CASE WHEN r.status='ACTIVE' THEN r.reg_id END) AS available, CASE WHEN e.seats=0 THEN 0 ELSE ROUND(100.0*COUNT(CASE WHEN r.status='ACTIVE' THEN r.reg_id END)/e.seats,1) END AS percentage FROM events e LEFT JOIN registrations r ON r.event_id=e.event_id GROUP BY e.event_id,e.name,e.seats ORDER BY e.event_date,e.name").fetchall()
    return render_template("summary.html", rows=rows)
