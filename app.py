from flask import Flask, render_template, request, redirect, url_for, session
from database import get_connection
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Get secret key from .env
app.secret_key = os.getenv("FLASK_SECRET_KEY")


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":

            session['user'] = username

            return redirect(url_for('dashboard'))

        else:
            return render_template(
                'login.html',
                error="Invalid username or password"
            )

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html')


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():

    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        roll_no = request.form['roll_no']
        name = request.form['name']
        department = request.form['department']
        semester = request.form['semester']
        email = request.form['email']
        phone = request.form['phone']

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO students
            (roll_no, name, department, semester, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            roll_no,
            name,
            department,
            semester,
            email,
            phone
        )

        cursor.execute(query, values)

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for('add_student'))

    return render_template('add_student.html')

@app.route('/students')
def students():

    if 'user' not in session:
        return redirect(url_for('login'))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT roll_no, name, department, semester, email, phone "
        "FROM students ORDER BY roll_no"
    )
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('students.html', students=students)

@app.route('/search_student', methods=['GET', 'POST'])
def search_student():

    if 'user' not in session:
        return redirect(url_for('login'))

    students = None

    if request.method == 'POST':

        search = request.form['search']

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT roll_no, name, department, semester, email, phone
            FROM students
            WHERE name LIKE %s OR roll_no LIKE %s
        """

        like_term = f"%{search}%"

        cursor.execute(query, (like_term, like_term))

        students = cursor.fetchall()

        cursor.close()
        connection.close()

    return render_template('search_student.html', students=students)

@app.route('/add_growth', methods=['GET', 'POST'])
def add_growth():

    if 'user' not in session:
        return redirect(url_for('login'))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT roll_no, name, department, semester "
        "FROM students ORDER BY roll_no"
    )
    students = cursor.fetchall()

    message = None

    if request.method == 'POST':

        roll_no = request.form['roll_no']
        semester = request.form['semester']
        marks = request.form['marks']

        cursor.execute(
            "INSERT INTO growth (roll_no, semester, marks) VALUES (%s, %s, %s)",
            (roll_no, semester, marks)
        )

        connection.commit()

        message = "Growth record added successfully."

    cursor.close()
    connection.close()

    return render_template(
        'add_growth.html',
        students=students,
        message=message
    )
    
@app.route('/growth_tracker', methods=['GET', 'POST'])
def growth_tracker():

    if 'user' not in session:
        return redirect(url_for('login'))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT roll_no, name FROM students")
    students = cursor.fetchall()

    selected_student = None
    growth_data = None

    if request.method == 'POST':

        roll_no = request.form['roll_no']

        cursor.execute(
            "SELECT roll_no, name FROM students WHERE roll_no = %s",
            (roll_no,)
        )
        selected_student = cursor.fetchone()

        cursor.execute(
            "SELECT semester, marks FROM growth WHERE roll_no = %s ORDER BY semester",
            (roll_no,)
        )
        growth_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'growth_tracker.html',
        students=students,
        selected_student=selected_student,
        growth_data=growth_data
    )

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)