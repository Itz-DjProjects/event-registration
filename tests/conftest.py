import pytest
from app import create_app

@pytest.fixture()
def app(tmp_path):
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False, "DATABASE": str(tmp_path / "test.db"), "SECRET_KEY": "test-secret"})
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def manager_id(app):
    from werkzeug.security import generate_password_hash
    from database.db import get_db_connection
    with app.app_context():
        conn = get_db_connection()
        cur = conn.execute("INSERT INTO managers(username,password_hash) VALUES(?,?)", ("manager", generate_password_hash("a-strong-test-password")))
        return cur.lastrowid
