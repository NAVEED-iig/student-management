import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")

import database
import app as flask_app_module


SCHEMA = """
CREATE TABLE students (
    roll_no TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    semester TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL
);

CREATE TABLE growth (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,
    semester TEXT NOT NULL,
    marks REAL NOT NULL,
    FOREIGN KEY (roll_no) REFERENCES students(roll_no)
);
"""


class SQLiteCursorWrapper:

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        query = query.replace("%s", "?")
        if params is None:
            return self._cursor.execute(query)
        return self._cursor.execute(query, params)

    def fetchall(self):
        return [dict(row) for row in self._cursor.fetchall()]

    def fetchone(self):
        row = self._cursor.fetchone()
        return dict(row) if row is not None else None

    def close(self):
        self._cursor.close()


class SQLiteConnectionWrapper:

    def __init__(self, connection):
        self._connection = connection

    def cursor(self, dictionary=False):
        return SQLiteCursorWrapper(self._connection.cursor())

    def commit(self):
        self._connection.commit()

    def close(self):
        pass


@pytest.fixture
def sqlite_connection():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    connection.commit()
    yield connection
    connection.close()


@pytest.fixture
def db_connection(sqlite_connection, monkeypatch):

    def fake_get_connection():
        return SQLiteConnectionWrapper(sqlite_connection)

    monkeypatch.setattr(database, "get_connection", fake_get_connection)
    monkeypatch.setattr(flask_app_module, "get_connection", fake_get_connection)

    return sqlite_connection


@pytest.fixture
def client(db_connection):
    flask_app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    with flask_app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def logged_in_client(client):
    with client.session_transaction() as session:
        session["user"] = "admin"
    return client