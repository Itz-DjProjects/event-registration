import getpass
import os
import secrets
import sqlite3
import sys
from pathlib import Path
from flask import Flask, flash, redirect, render_template, request, session, url_for, abort
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config
from database.db import close_db, initialize_database, get_db_connection
from routes.student import student_bp
from routes.manager import manager_bp
from routes.auth import auth_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    # Config is imported before the local entry point creates its ephemeral key.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        if app.testing:
            app.config["SECRET_KEY"] = "test-only-secret"
        else:
            raise RuntimeError("Set SECRET_KEY in the environment before starting the app. See .env.example.")
    CSRFProtect(app)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    initialize_database(app.config["DATABASE"])
    app.teardown_appcontext(close_db)
    app.register_blueprint(student_bp)
    app.register_blueprint(manager_bp, url_prefix="/manager")
    app.register_blueprint(auth_bp, url_prefix="/manager")

    @app.errorhandler(400)
    def bad_request(_error):
        return render_template("error.html", message="The request could not be processed. Please refresh and try again."), 400

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", message="The page or record you requested was not found."), 404

    @app.errorhandler(500)
    def server_error(_error):
        app.logger.exception("Unhandled application error")
        return render_template("error.html", message="Something went wrong. Please try again."), 500
    return app


def create_manager():
    initialize_database()
    username = input("Manager username: ").strip()
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")
    if not username or len(username) > 80:
        raise SystemExit("Username must be 1–80 characters.")
    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters.")
    if password != confirm:
        raise SystemExit("Passwords do not match.")
    conn = sqlite3.connect(Config.DATABASE)
    try:
        conn.execute("INSERT INTO managers(username,password_hash) VALUES(?,?)", (username, generate_password_hash(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        raise SystemExit("That manager username already exists.")
    finally:
        conn.close()
    print("Manager account created.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create-manager":
        create_manager()
    else:
        # Convenient local startup; production/WSGI deployments must provide a stable secret.
        if not os.environ.get("SECRET_KEY"):
            os.environ["SECRET_KEY"] = secrets.token_hex(32)
        create_app().run(debug=os.environ.get("FLASK_DEBUG") == "1")
