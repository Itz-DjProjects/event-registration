from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from database.db import get_db_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        manager = get_db_connection().execute("SELECT manager_id,username,password_hash FROM managers WHERE username=?", (username,)).fetchone()
        if manager and check_password_hash(manager["password_hash"], password):
            session.clear()
            session["manager_id"] = manager["manager_id"]
            session["manager_username"] = manager["username"]
            return redirect(url_for("manager.dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("manager_login.html")

@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("student.index"))
