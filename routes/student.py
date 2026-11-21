from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from database.db import get_db_connection
from services.event_service import list_events, get_event
from services.registration_service import register_student, cancel_registration, registrations_for_roll

student_bp = Blueprint("student", __name__)

@student_bp.get("/")
def index():
    return render_template("index.html", events=list_events()[:3])

@student_bp.get("/events")
def events():
    return render_template("events.html", events=list_events())

@student_bp.get("/events/<int:event_id>")
def event_detail(event_id):
    event = get_event(event_id)
    if event is None: abort(404)
    return render_template("event_detail.html", event=event)

@student_bp.route("/events/<int:event_id>/register", methods=["GET", "POST"])
def register(event_id):
    event = get_event(event_id)
    if event is None: abort(404)
    if request.method == "POST":
        try:
            reg_id = register_student(event_id, request.form.get("student_name"), request.form.get("roll_no"))
            return render_template("registration_success.html", reg_id=reg_id, event=event)
        except (ValueError, LookupError) as exc:
            flash(str(exc), "error")
    return render_template("register.html", event=event)

@student_bp.route("/my-registrations", methods=["GET", "POST"])
def my_registrations():
    roll = request.values.get("roll_no", "").strip()
    rows = registrations_for_roll(roll) if roll else []
    return render_template("my_registrations.html", registrations=rows, roll_no=roll)

@student_bp.post("/registrations/<int:reg_id>/cancel")
def cancel(reg_id):
    roll = request.form.get("roll_no", "").strip()
    try:
        cancel_registration(reg_id, roll)
        flash("Registration cancelled and your seat released.", "success")
    except (ValueError, LookupError) as exc:
        flash(str(exc), "error")
    return redirect(url_for("student.my_registrations", roll_no=roll))
