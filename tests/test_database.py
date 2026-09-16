import sqlite3

import pytest

import database


def test_students_table_created(sqlite_connection):
    row = sqlite_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='students'"
    ).fetchone()
    assert row is not None


def test_growth_table_created(sqlite_connection):
    row = sqlite_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='growth'"
    ).fetchone()
    assert row is not None


def test_insert_and_fetch_student(sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("101", "Rahul", "CSE", "5", "rahul@example.com", "9999999999")
    )
    sqlite_connection.commit()

    row = sqlite_connection.execute(
        "SELECT * FROM students WHERE roll_no = ?", ("101",)
    ).fetchone()

    assert row["name"] == "Rahul"
    assert row["department"] == "CSE"


def test_duplicate_roll_no_raises_integrity_error(sqlite_connection):
    student = ("101", "Rahul", "CSE", "5", "rahul@example.com", "9999999999")

    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)", student
    )
    sqlite_connection.commit()

    with pytest.raises(sqlite3.IntegrityError):
        sqlite_connection.execute(
            "INSERT INTO students (roll_no, name, department, semester, email, phone) "
            "VALUES (?, ?, ?, ?, ?, ?)", student
        )


def test_insert_and_fetch_growth_records(sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("102", "Priya", "IT", "4", "priya@example.com", "8888888888")
    )

    sqlite_connection.executemany(
        "INSERT INTO growth (roll_no, semester, marks) VALUES (?, ?, ?)",
        [("102", "1", 72), ("102", "2", 78), ("102", "3", 85)]
    )
    sqlite_connection.commit()

    rows = sqlite_connection.execute(
        "SELECT semester, marks FROM growth WHERE roll_no = ? ORDER BY semester",
        ("102",)
    ).fetchall()

    assert [dict(r) for r in rows] == [
        {"semester": "1", "marks": 72},
        {"semester": "2", "marks": 78},
        {"semester": "3", "marks": 85},
    ]


def test_growth_query_returns_empty_for_unknown_student(sqlite_connection):
    rows = sqlite_connection.execute(
        "SELECT semester, marks FROM growth WHERE roll_no = ?", ("999",)
    ).fetchall()

    assert rows == []


def test_get_connection_passes_env_vars_to_mysql_connector(monkeypatch):
    captured = {}

    def fake_connect(**kwargs):
        captured.update(kwargs)
        return "fake-connection"

    monkeypatch.setattr(database.mysql.connector, "connect", fake_connect)
    monkeypatch.setenv("MYSQL_HOST", "localhost")
    monkeypatch.setenv("MYSQL_USER", "test_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "test_pass")
    monkeypatch.setenv("MYSQL_DATABASE", "test_db")

    connection = database.get_connection()

    assert connection == "fake-connection"
    assert captured == {
        "host": "localhost",
        "user": "test_user",
        "password": "test_pass",
        "database": "test_db",
    }


def test_get_connection_returns_mysql_connector_result(monkeypatch):
    monkeypatch.setattr(
        database.mysql.connector, "connect", lambda **kwargs: "connected"
    )

    assert database.get_connection() == "connected"