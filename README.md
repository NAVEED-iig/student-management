# Student Management System
A basic student management website to easily track student data.

## How to run the project

### 1. Clone the repository
```bash
git clone https://github.com/gituser_name/student-management.git
cd student-management
```

### 2. Create and activate the virtual environment
```bash
python -m venv myvenv
# On Windows
myvenv\Scripts\activate
# On Linux/Mac
source myvenv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

### 5. Set up the MySQL database
Run the following SQL commands in your MySQL client:
```sql
CREATE TABLE students (
    roll_no VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    semester VARCHAR(10) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL
);

CREATE TABLE growth (
    id INT PRIMARY KEY AUTO_INCREMENT,
    roll_no VARCHAR(20) NOT NULL,
    semester VARCHAR(10) NOT NULL,
    marks DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (roll_no) REFERENCES students(roll_no)
);
```

### 6. In the terminal 
```bash
python app.py
```

### 7. If you want test the codebase
```bash 
pip install pytest
```

### 8. Code Coverage
```bash
cd tests
pytest -v
pytest --cov=. --cov-report=xml
pytest --cov=. --cov-fail-under=85
pytest --cov=. --cov-report=term --cov-report=xml --cov-fail-under=85 -v
```