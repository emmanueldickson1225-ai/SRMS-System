from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql

app = Flask(__name__)
app.secret_key = "srms_secret_key"

# ================= DATABASE =================
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="srms"
    )

# ================= LOGIN PAGE =================
@app.route('/')
def login():
    return render_template("login.html")

# ================= LOGIN PROCESS =================
@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        session['user'] = username
        session['role'] = user[2] if len(user) > 2 else "admin"
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid username or password", "danger")
        return redirect(url_for('login'))

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    conn.close()

    return render_template("dashboard.html", total_students=total_students)

# ================= REGISTER FORM =================
@app.route('/register-form')
def register_form():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template("register.html")

# ================= REGISTER STUDENT =================
@app.route('/register', methods=['POST'])
def register_student():
    full_name = request.form['full_name']
    reg_no = request.form['reg_no']
    course = request.form['course']
    gender = request.form['gender']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (full_name, reg_no, course, gender) VALUES (%s, %s, %s, %s)",
        (full_name, reg_no, course, gender)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('students'))

# ================= VIEW STUDENTS =================
@app.route('/students')
def students():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    conn.close()

    return render_template("students.html", students=data)

# ================= DELETE STUDENT =================
@app.route('/delete/<int:id>')
def delete_student(id):

    if 'user' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        return "Access Denied"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('students'))

# ================= EDIT STUDENT =================
@app.route('/edit/<int:id>')
def edit_student(id):

    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()

    conn.close()

    return render_template("edit.html", student=student)

# ================= UPDATE STUDENT =================
@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):

    full_name = request.form['full_name']
    reg_no = request.form['reg_no']
    course = request.form['course']
    gender = request.form['gender']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students 
        SET full_name=%s, reg_no=%s, course=%s, gender=%s 
        WHERE id=%s
    """, (full_name, reg_no, course, gender, id))

    conn.commit()
    conn.close()

    return redirect(url_for('students'))

# ================= RUN APP =================
if __name__ == '__main__':
    app.run(debug=True)