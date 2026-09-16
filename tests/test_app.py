def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_success_redirects_to_dashboard(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "1234"},
        follow_redirects=False
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_login_failure_shows_error(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_dashboard_loads_when_logged_in(logged_in_client):
    response = logged_in_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data



def test_add_student_creates_record(logged_in_client, sqlite_connection):
    response = logged_in_client.post(
        "/add_student",
        data={
            "roll_no": "201",
            "name": "Arun",
            "department": "Mechanical",
            "semester": "6",
            "email": "arun@example.com",
            "phone": "7777777777"
        },
        follow_redirects=False
    )

    assert response.status_code == 302

    row = sqlite_connection.execute(
        "SELECT * FROM students WHERE roll_no = ?", ("201",)
    ).fetchone()

    assert row["name"] == "Arun"


def test_search_student_finds_match(logged_in_client, sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("301", "Meera", "ECE", "3", "meera@example.com", "6666666666")
    )
    sqlite_connection.commit()

    response = logged_in_client.post("/search_student", data={"search": "Meera"})

    assert response.status_code == 200
    assert b"Meera" in response.data


def test_search_student_no_match(logged_in_client):
    response = logged_in_client.post("/search_student", data={"search": "Nobody"})

    assert response.status_code == 200
    assert "No student found".encode() in response.data


def test_growth_tracker_lists_students(logged_in_client, sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("401", "Kiran", "CSE", "5", "kiran@example.com", "5555555555")
    )
    sqlite_connection.commit()

    response = logged_in_client.get("/growth_tracker")

    assert response.status_code == 200
    assert b"Kiran" in response.data


def test_growth_tracker_shows_marks_for_selected_student(logged_in_client, sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("402", "Divya", "CSE", "5", "divya@example.com", "4444444444")
    )
    sqlite_connection.executemany(
        "INSERT INTO growth (roll_no, semester, marks) VALUES (?, ?, ?)",
        [("402", "1", 80), ("402", "2", 90)]
    )
    sqlite_connection.commit()

    response = logged_in_client.post("/growth_tracker", data={"roll_no": "402"})

    assert response.status_code == 200
    assert b"Divya" in response.data
    assert b"90" in response.data


def test_growth_tracker_no_data_message(logged_in_client, sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("403", "Sameer", "CSE", "5", "sameer@example.com", "3333333333")
    )
    sqlite_connection.commit()

    response = logged_in_client.post("/growth_tracker", data={"roll_no": "403"})

    assert response.status_code == 200
    assert b"No growth data available" in response.data


def test_logout_clears_session(logged_in_client):
    response = logged_in_client.get("/logout", follow_redirects=False)
    assert response.status_code == 302

    dashboard_response = logged_in_client.get("/dashboard", follow_redirects=False)
    assert dashboard_response.status_code == 302


def test_students_page_requires_login(client):
    response = client.get("/students", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_students_page_lists_all_students(logged_in_client, sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("701", "Ishaan", "ECE", "4", "ishaan@example.com", "9090909090")
    )
    sqlite_connection.commit()

    response = logged_in_client.get("/students")

    assert response.status_code == 200
    assert b"Ishaan" in response.data
    assert b"ishaan@example.com" in response.data


def test_students_page_shows_message_when_empty(logged_in_client):
    response = logged_in_client.get("/students")

    assert response.status_code == 200
    assert b"No students found" in response.data


def test_add_growth_requires_login(client):
    response = client.get("/add_growth", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_add_growth_get_lists_students(logged_in_client, sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("501", "Neha", "CSE", "3", "neha@example.com", "1112223333")
    )
    sqlite_connection.commit()

    response = logged_in_client.get("/add_growth")

    assert response.status_code == 200
    assert b"Neha" in response.data


def test_add_growth_post_inserts_record(logged_in_client, sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("502", "Vikram", "IT", "2", "vikram@example.com", "4445556666")
    )
    sqlite_connection.commit()

    response = logged_in_client.post(
        "/add_growth",
        data={"roll_no": "502", "semester": "2", "marks": "88"}
    )

    assert response.status_code == 200
    assert b"Growth record added successfully" in response.data

    row = sqlite_connection.execute(
        "SELECT * FROM growth WHERE roll_no = ?", ("502",)
    ).fetchone()

    assert row["semester"] == "2"
    assert row["marks"] == 88


def test_add_growth_reflects_in_growth_tracker(logged_in_client, sqlite_connection):
    sqlite_connection.execute(
        "INSERT INTO students (roll_no, name, department, semester, email, phone) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("503", "Zoya", "IT", "3", "zoya@example.com", "7778889999")
    )
    sqlite_connection.commit()

    logged_in_client.post(
        "/add_growth",
        data={"roll_no": "503", "semester": "3", "marks": "77"}
    )

    response = logged_in_client.post("/growth_tracker", data={"roll_no": "503"})

    assert response.status_code == 200
    assert b"Zoya" in response.data
    assert b"77" in response.data