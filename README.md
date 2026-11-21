# Campus Event Registration System

A Flask and SQLite application for managing campus events and preventing registrations from exceeding seat capacity. Students can register, look up registrations by roll number, and cancel. Managers can maintain events, review participants, and view SQL-based registration statistics.

## Features

- Public event listings, details, student registration and cancellation
- Atomic seat management with SQLite `BEGIN IMMEDIATE`
- Manager login with Werkzeug password hashes and session authentication
- CSRF protection on forms that change data
- Event creation, editing, participant lists and guarded deletion
- Summary page using `LEFT JOIN`, `GROUP BY` and `COUNT`-style aggregation
- Isolated pytest database for automated tests

## Technology

Python 3, Flask, Flask-WTF, SQLite, Jinja2, Werkzeug and pytest.

## Project structure

`app.py` and `config.py` configure the application; `database/` contains schema and connections; `routes/` contains blueprints; `services/` holds event and registration rules; `templates/` and `static/` provide the interface; `tests/` contains automated tests. The default database is stored in `instance/events.db`.

## Ubuntu setup

```bash
sudo apt update
sudo apt install python3 python3-venv
cd event-registration
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If your shell is Fish, use `source .venv/bin/activate.fish` instead. You can also skip activation and run commands directly as `.venv/bin/python app.py` and `.venv/bin/python -m pip install -r requirements.txt`.

`python app.py` generates an ephemeral key for convenient local use when `SECRET_KEY` is unset. For a stable development session or deployment, set a secret key before starting. Create `.env` from `.env.example` and export its values in your shell (the app does not load `.env` automatically):

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

## Database initialization

The schema initializes automatically when the application starts, and `CREATE TABLE IF NOT EXISTS` preserves existing records. No seed data or default manager account is created.

## Create a manager

```bash
python app.py create-manager
```

The CLI asks for a username and securely prompts for a password twice. Passwords must be at least 12 characters.

## Start the application

```bash
python app.py
```

Open `http://127.0.0.1:5000`. Set `FLASK_DEBUG=1` only for local development. For deployment, use a production WSGI server and HTTPS; set `COOKIE_SECURE=1` when serving over HTTPS.

## Run tests

```bash
pytest
```

Tests use a temporary SQLite database configured per test and do not modify the development database.
