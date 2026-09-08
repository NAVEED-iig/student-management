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


@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)