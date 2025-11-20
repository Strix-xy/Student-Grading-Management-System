from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['DATABASE'] = 'grading_system.db'

# Database initialization
def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Users table (teachers/admins)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'teacher',
        education_level TEXT DEFAULT 'Secondary',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Add education_level column if it doesn't exist
    try:
        c.execute('ALTER TABLE users ADD COLUMN education_level TEXT DEFAULT "Secondary"')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        section TEXT NOT NULL,
        year_level TEXT NOT NULL,
        education_level TEXT NOT NULL DEFAULT 'Secondary',
        school_year TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Add education_level column if it doesn't exist
    try:
        c.execute('ALTER TABLE students ADD COLUMN education_level TEXT NOT NULL DEFAULT "Secondary"')
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Add school_year column if it doesn't exist
    try:
        c.execute('ALTER TABLE students ADD COLUMN school_year TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass
    # Add teacher_id column if it doesn't exist
    try:
        c.execute('ALTER TABLE students ADD COLUMN teacher_id INTEGER DEFAULT NULL')
    except sqlite3.OperationalError:
        pass
    
    # Subjects table
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT UNIQUE NOT NULL,
        subject_name TEXT NOT NULL,
        description TEXT,
        units INTEGER NOT NULL DEFAULT 3,
        education_level TEXT NOT NULL DEFAULT 'Secondary',
        class_year TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Add education_level column if it doesn't exist
    try:
        c.execute('ALTER TABLE subjects ADD COLUMN education_level TEXT NOT NULL DEFAULT "Secondary"')
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Add class_year column if it doesn't exist
    try:
        c.execute('ALTER TABLE subjects ADD COLUMN class_year TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass
    # Add teacher_id column if it doesn't exist
    try:
        c.execute('ALTER TABLE subjects ADD COLUMN teacher_id INTEGER DEFAULT NULL')
    except sqlite3.OperationalError:
        pass
    
    # Grades table
    c.execute('''CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        quarter TEXT NOT NULL,
        prelim REAL DEFAULT 0,
        midterm REAL DEFAULT 0,
        finals REAL DEFAULT 0,
        final_grade REAL DEFAULT 0,
        remarks TEXT,
        teacher_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (subject_id) REFERENCES subjects (id),
        FOREIGN KEY (teacher_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

# Database helper functions
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        education_level = request.form.get('education_level', 'Primary') or 'Primary'
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (username, email, password, role, education_level) VALUES (?, ?, ?, ?, ?)',
                        (username, email, hashed_password, 'teacher', education_level))
            conn.commit()
            conn.close()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['education_level'] = user['education_level']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    conn = get_db()

    # Scope by education level for non-admin users
    edu_level = session.get('education_level')
    is_admin = session.get('role') == 'admin'

    # Get statistics
    teacher_id = session.get('user_id')
    if is_admin or not edu_level:
        total_students = conn.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
        total_subjects = conn.execute('SELECT COUNT(*) as count FROM subjects').fetchone()['count']
        total_grades = conn.execute('SELECT COUNT(*) as count FROM grades').fetchone()['count']
    else:
        total_students = conn.execute('SELECT COUNT(*) as count FROM students WHERE education_level = ? AND teacher_id = ?', (edu_level, teacher_id)).fetchone()['count']
        total_subjects = conn.execute('SELECT COUNT(*) as count FROM subjects WHERE education_level = ? AND teacher_id = ?', (edu_level, teacher_id)).fetchone()['count']
        # join grades -> students to scope grades by student education level and teacher
        total_grades = conn.execute('''SELECT COUNT(*) as count FROM grades g JOIN students s ON g.student_id = s.id WHERE s.education_level = ? AND s.teacher_id = ?''', (edu_level, teacher_id)).fetchone()['count']

    # Get recent grades with student and subject info
    # Include student section, year_level and education_level and subject class_year for client-side filtering
    if is_admin or not edu_level:
        recent_grades = conn.execute('''
            SELECT g.*, s.first_name, s.last_name, s.student_id as sid, s.section as student_section, s.year_level as student_year_level, s.education_level as student_education_level, s.school_year as student_school_year, sub.subject_name, sub.subject_code, sub.class_year as subject_class_year
            FROM grades g
            JOIN students s ON g.student_id = s.id
            JOIN subjects sub ON g.subject_id = sub.id
            ORDER BY g.updated_at DESC
            LIMIT 10
        ''').fetchall()
    else:
        recent_grades = conn.execute('''
            SELECT g.*, s.first_name, s.last_name, s.student_id as sid, s.section as student_section, s.year_level as student_year_level, s.education_level as student_education_level, s.school_year as student_school_year, sub.subject_name, sub.subject_code, sub.class_year as subject_class_year
            FROM grades g
            JOIN students s ON g.student_id = s.id
            JOIN subjects sub ON g.subject_id = sub.id
            WHERE s.education_level = ? AND s.teacher_id = ?
            ORDER BY g.updated_at DESC
            LIMIT 10
        ''', (edu_level, teacher_id)).fetchall()


    # Provide students and subjects for dashboard selectors (scoped)
    if is_admin or not edu_level:
        dashboard_students = conn.execute('SELECT * FROM students ORDER BY last_name, first_name').fetchall()
        dashboard_subjects = conn.execute('SELECT * FROM subjects ORDER BY subject_code').fetchall()
    else:
        dashboard_students = conn.execute('SELECT * FROM students WHERE education_level = ? AND teacher_id = ? ORDER BY last_name, first_name', (edu_level, teacher_id)).fetchall()
        dashboard_subjects = conn.execute('SELECT * FROM subjects WHERE education_level = ? AND teacher_id = ? ORDER BY subject_code', (edu_level, teacher_id)).fetchall()

    conn.close()

    return render_template('dashboard.html', 
                         total_students=total_students,
                         total_subjects=total_subjects,
                         total_grades=total_grades,
                         recent_grades=[dict(g) for g in recent_grades],
                         dashboard_students=[dict(s) for s in dashboard_students],
                         dashboard_subjects=[dict(s) for s in dashboard_subjects])


@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute('SELECT id, username, email, role, education_level, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not user:
        flash('User not found. Please log in again.', 'warning')
        session.clear()
        return redirect(url_for('login'))
    return render_template('profile.html', user=dict(user))


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        education_level = request.form.get('education_level', 'Secondary')
        password = request.form.get('password', '').strip()

        try:
            if password:
                hashed = generate_password_hash(password)
                conn.execute('''UPDATE users SET username = ?, email = ?, education_level = ?, password = ? WHERE id = ?''',
                             (username, email, education_level, hashed, user_id))
            else:
                conn.execute('''UPDATE users SET username = ?, email = ?, education_level = ? WHERE id = ?''',
                             (username, email, education_level, user_id))
            conn.commit()
            # Refresh session values
            session['username'] = username
            session['education_level'] = education_level
            flash('Profile updated successfully!', 'success')
            conn.close()
            return redirect(url_for('profile'))
        except sqlite3.IntegrityError:
            flash('Username or email already in use!', 'danger')

    user = conn.execute('SELECT id, username, email, education_level FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not user:
        flash('User not found. Please log in again.', 'warning')
        session.clear()
        return redirect(url_for('login'))
    return render_template('edit_profile.html', user=dict(user))

@app.route('/students')
@login_required
def students():
    """View all students"""
    conn = get_db()
    # Scope students to user's education level unless admin
    edu_level = session.get('education_level')
    is_admin = session.get('role') == 'admin'
    teacher_id = session.get('user_id')
    if is_admin or not edu_level:
        students = conn.execute('SELECT * FROM students ORDER BY last_name, first_name').fetchall()
    else:
        students = conn.execute('SELECT * FROM students WHERE education_level = ? AND teacher_id = ? ORDER BY last_name, first_name', (edu_level, teacher_id)).fetchall()
    conn.close()
    # Convert Row objects to dictionaries for JSON serialization
    students_list = [dict(student) for student in students]
    return render_template('students.html', students=students_list)

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add new student"""
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        section = request.form.get('section')
        year_level = request.form.get('year_level')
        education_level = request.form.get('education_level', 'Secondary')
        school_year = request.form.get('school_year', '')
        
        try:
            conn = get_db()
            conn.execute('''INSERT INTO students (student_id, first_name, last_name, email, section, year_level, education_level, school_year, teacher_id)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (student_id, first_name, last_name, email, section, year_level, education_level, school_year, session['user_id']))
            conn.commit()
            conn.close()
            flash('Student added successfully!', 'success')
            return redirect(url_for('students'))
        except sqlite3.IntegrityError:
            flash('Student ID or email already exists!', 'danger')
    
    return render_template('add_student.html')


@app.route('/students/view/<int:student_id>')
@login_required
def view_student(student_id):
    conn = get_db()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    if not student:
        flash('Student not found.', 'warning')
        return redirect(url_for('students'))
    return render_template('view_student.html', student=dict(student))


@app.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    conn = get_db()
    if request.method == 'POST':
        student_id_form = request.form.get('student_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        section = request.form.get('section')
        year_level = request.form.get('year_level')
        education_level = request.form.get('education_level', 'Secondary')
        school_year = request.form.get('school_year', '')

        try:
            conn.execute('''UPDATE students SET student_id = ?, first_name = ?, last_name = ?, email = ?, section = ?, year_level = ?, education_level = ?, school_year = ?, teacher_id = ? WHERE id = ?''',
                         (student_id_form, first_name, last_name, email, section, year_level, education_level, school_year, session['user_id'], student_id))
            conn.commit()
            conn.close()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('students'))
        except sqlite3.IntegrityError:
            flash('Student ID or email already exists!', 'danger')

    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    if not student:
        flash('Student not found.', 'warning')
        return redirect(url_for('students'))
    return render_template('edit_student.html', student=dict(student))


@app.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    conn = get_db()
    conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    flash('Student deleted successfully!', 'success')
    return ('', 204)

@app.route('/subjects')
@login_required
def subjects():
    """View all subjects"""
    conn = get_db()
    # Scope subjects to user's education level unless admin
    edu_level = session.get('education_level')
    is_admin = session.get('role') == 'admin'
    teacher_id = session.get('user_id')
    if is_admin or not edu_level:
        subjects = conn.execute('SELECT * FROM subjects ORDER BY subject_code').fetchall()
    else:
        subjects = conn.execute('SELECT * FROM subjects WHERE education_level = ? AND teacher_id = ? ORDER BY subject_code', (edu_level, teacher_id)).fetchall()
    conn.close()
    # Convert Row objects to dictionaries for JSON serialization
    subjects_list = [dict(subject) for subject in subjects]
    return render_template('subjects.html', subjects=subjects_list)

@app.route('/subjects/add', methods=['GET', 'POST'])
@login_required
def add_subject():
    """Add new subject"""
    if request.method == 'POST':
        subject_code = request.form.get('subject_code')
        subject_name = request.form.get('subject_name')
        description = request.form.get('description')
        units = request.form.get('units')
        education_level = request.form.get('education_level', 'Secondary')
        class_year = request.form.get('class_year', '')
        
        try:
            conn = get_db()
            conn.execute('''INSERT INTO subjects (subject_code, subject_name, description, units, education_level, class_year, teacher_id)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (subject_code, subject_name, description, units, education_level, class_year, session['user_id']))
            conn.commit()
            conn.close()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('subjects'))
        except sqlite3.IntegrityError:
            flash('Subject code already exists!', 'danger')
    
    return render_template('add_subject.html')


@app.route('/subjects/view/<int:subject_id>')
@login_required
def view_subject(subject_id):
    conn = get_db()
    subject = conn.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,)).fetchone()
    conn.close()
    if not subject:
        flash('Subject not found.', 'warning')
        return redirect(url_for('subjects'))
    return render_template('view_subject.html', subject=dict(subject))


@app.route('/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    conn = get_db()
    if request.method == 'POST':
        subject_code = request.form.get('subject_code')
        subject_name = request.form.get('subject_name')
        description = request.form.get('description')
        units = request.form.get('units', 3)
        education_level = request.form.get('education_level', 'Secondary')
        class_year = request.form.get('class_year', '')

        try:
            conn.execute('''UPDATE subjects SET subject_code = ?, subject_name = ?, description = ?, units = ?, education_level = ?, class_year = ?, teacher_id = ? WHERE id = ?''',
                         (subject_code, subject_name, description, units, education_level, class_year, session['user_id'], subject_id))
            conn.commit()
            conn.close()
            flash('Subject updated successfully!', 'success')
            return redirect(url_for('subjects'))
        except sqlite3.IntegrityError:
            flash('Subject code already exists!', 'danger')

    subject = conn.execute('SELECT * FROM subjects WHERE id = ?', (subject_id,)).fetchone()
    conn.close()
    if not subject:
        flash('Subject not found.', 'warning')
        return redirect(url_for('subjects'))
    return render_template('edit_subject.html', subject=dict(subject))


@app.route('/subjects/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    conn = get_db()
    conn.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
    conn.commit()
    conn.close()
    flash('Subject deleted successfully!', 'success')
    return ('', 204)

@app.route('/grades')
@login_required
def grades():
    """View all grades"""
    conn = get_db()
    
    # Get statistics scoped by education level for non-admin users
    edu_level = session.get('education_level')
    is_admin = session.get('role') == 'admin'
    
    if is_admin or not edu_level:
        total_students = conn.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
        total_subjects = conn.execute('SELECT COUNT(*) as count FROM subjects').fetchone()['count']
        total_grades = conn.execute('SELECT COUNT(*) as count FROM grades').fetchone()['count']
    else:
        total_students = conn.execute('SELECT COUNT(*) as count FROM students WHERE education_level = ?', (edu_level,)).fetchone()['count']
        total_subjects = conn.execute('SELECT COUNT(*) as count FROM subjects WHERE education_level = ?', (edu_level,)).fetchone()['count']
        total_grades = conn.execute('''SELECT COUNT(*) as count FROM grades g JOIN students s ON g.student_id = s.id WHERE s.education_level = ?''', (edu_level,)).fetchone()['count']
    
    # Build base query and parameters
    params = []
    base_query = '''
        SELECT g.*, s.first_name, s.last_name, s.student_id as sid, s.education_level as education_level, s.year_level as year_level, sub.subject_name, sub.subject_code
        FROM grades g
        JOIN students s ON g.student_id = s.id
        JOIN subjects sub ON g.subject_id = sub.id
    '''

    # Apply scoping by user education_level unless admin
    edu_level = session.get('education_level')
    is_admin = session.get('role') == 'admin'
    where_clauses = []
    teacher_id = session.get('user_id')
    if not is_admin and edu_level:
        where_clauses.append('s.education_level = ?')
        params.append(edu_level)
        where_clauses.append('s.teacher_id = ?')
        params.append(teacher_id)

    # Accept optional filters from query params
    student_filter = request.args.get('student_id')
    subject_filter = request.args.get('subject_id')
    if student_filter:
        where_clauses.append('s.id = ?')
        params.append(student_filter)
    if subject_filter:
        where_clauses.append('sub.id = ?')
        params.append(subject_filter)

    if where_clauses:
        base_query += ' WHERE ' + ' AND '.join(where_clauses)

    base_query += ' ORDER BY g.updated_at DESC'

    grades = conn.execute(base_query, tuple(params)).fetchall()

    conn.close()

    # Convert Row objects to dictionaries for JSON serialization
    grades_list = [dict(grade) for grade in grades]
    return render_template('grades.html', grades=grades_list)

@app.route('/grades/add', methods=['GET', 'POST'])
@login_required
def add_grade():
    """Add new grade"""
    conn = get_db()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject_id = request.form.get('subject_id')
        quarter = request.form.get('quarter')
        prelim = float(request.form.get('prelim', 0))
        midterm = float(request.form.get('midterm', 0))
        finals = float(request.form.get('finals', 0))
        
        # Determine student's education level to compute final grade correctly
        student_row = conn.execute('SELECT education_level FROM students WHERE id = ?', (student_id,)).fetchone()
        student_edu = student_row['education_level'] if student_row else 'Secondary'

        # Calculate final grade: tertiary uses midterm & finals average, others use 3-term average
        if student_edu == 'Tertiary':
            final_grade = (midterm + finals) / 2
        else:
            final_grade = (prelim + midterm + finals) / 3
        remarks = 'PASSED' if final_grade >= 75 else 'FAILED'
        
        conn.execute('''INSERT INTO grades (student_id, subject_id, quarter, prelim, midterm, finals, final_grade, remarks, teacher_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (student_id, subject_id, quarter, prelim, midterm, finals, final_grade, remarks, session['user_id']))
        conn.commit()
        conn.close()
        flash('Grade added successfully!', 'success')
        return redirect(url_for('grades'))
    
    # Provide students and subjects scoped by user education_level unless admin
    edu_level = session.get('education_level')
    is_admin = session.get('role') == 'admin'
    teacher_id = session.get('user_id')
    if is_admin or not edu_level:
        students = conn.execute('SELECT * FROM students ORDER BY last_name, first_name').fetchall()
        subjects = conn.execute('SELECT * FROM subjects ORDER BY subject_code').fetchall()
    else:
        students = conn.execute('SELECT * FROM students WHERE education_level = ? AND teacher_id = ? ORDER BY last_name, first_name', (edu_level, teacher_id)).fetchall()
        subjects = conn.execute('SELECT * FROM subjects WHERE education_level = ? AND teacher_id = ? ORDER BY subject_code', (edu_level, teacher_id)).fetchall()
    conn.close()

    students_list = [dict(s) for s in students]
    subjects_list = [dict(s) for s in subjects]

    return render_template('add_grade.html', students=students_list, subjects=subjects_list)

@app.route('/grades/edit/<int:grade_id>', methods=['GET', 'POST'])
@login_required
def edit_grade(grade_id):
    """Edit existing grade"""
    conn = get_db()
    
    if request.method == 'POST':
        prelim = float(request.form.get('prelim', 0))
        midterm = float(request.form.get('midterm', 0))
        finals = float(request.form.get('finals', 0))
        # Determine if this grade belongs to a tertiary student to compute correctly
        row = conn.execute('SELECT g.student_id, s.education_level FROM grades g JOIN students s ON g.student_id = s.id WHERE g.id = ?', (grade_id,)).fetchone()
        student_edu = row['education_level'] if row else 'Secondary'

        if student_edu == 'Tertiary':
            final_grade = (midterm + finals) / 2
        else:
            final_grade = (prelim + midterm + finals) / 3
        remarks = 'PASSED' if final_grade >= 75 else 'FAILED'
        
        conn.execute('''UPDATE grades 
                       SET prelim = ?, midterm = ?, finals = ?, final_grade = ?, remarks = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?''',
                    (prelim, midterm, finals, final_grade, remarks, grade_id))
        conn.commit()
        conn.close()
        flash('Grade updated successfully!', 'success')
        return redirect(url_for('grades'))
    
    grade = conn.execute('''
        SELECT g.*, s.first_name, s.last_name, sub.subject_name
        FROM grades g
        JOIN students s ON g.student_id = s.id
        JOIN subjects sub ON g.subject_id = sub.id
        WHERE g.id = ?
    ''', (grade_id,)).fetchone()
    conn.close()
    
    return render_template('edit_grade.html', grade=dict(grade))

@app.route('/grades/delete/<int:grade_id>', methods=['POST'])
@login_required
def delete_grade(grade_id):
    """Delete grade"""
    conn = get_db()
    conn.execute('DELETE FROM grades WHERE id = ?', (grade_id,))
    conn.commit()
    conn.close()
    flash('Grade deleted successfully!', 'success')
    return redirect(url_for('grades'))

# API endpoints
@app.route('/api/students/search')
@login_required
def search_students():
    """Search students API"""
    query = request.args.get('q', '')
    conn = get_db()
    # Scope search by user's education level unless admin
    edu_level = session.get('education_level')
    is_admin = session.get('role') == 'admin'
    params = [f'%{query}%', f'%{query}%', f'%{query}%']
    sql = '''
        SELECT * FROM students
        WHERE (first_name LIKE ? OR last_name LIKE ? OR student_id LIKE ?)
    '''
    if not is_admin and edu_level:
        sql += ' AND education_level = ?'
        params.append(edu_level)
    sql += ' ORDER BY last_name, first_name LIMIT 10'
    students = conn.execute(sql, tuple(params)).fetchall()
    conn.close()

    return jsonify([dict(s) for s in students])

@app.route('/api/stats')
@login_required
def api_stats():
    """Get statistics API"""
    conn = get_db()
    # Scope stats by education level for non-admin users
    edu_level = session.get('education_level')
    is_admin = session.get('role') == 'admin'

    teacher_id = session.get('user_id')
    if is_admin or not edu_level:
        total_students = conn.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
        total_subjects = conn.execute('SELECT COUNT(*) as count FROM subjects').fetchone()['count']
        total_grades = conn.execute('SELECT COUNT(*) as count FROM grades').fetchone()['count']
        avg_grade = conn.execute('SELECT AVG(final_grade) as avg FROM grades').fetchone()['avg'] or 0
        passed = conn.execute('SELECT COUNT(*) as count FROM grades WHERE final_grade >= 75').fetchone()['count']
    else:
        total_students = conn.execute('SELECT COUNT(*) as count FROM students WHERE education_level = ? AND teacher_id = ?', (edu_level, teacher_id)).fetchone()['count']
        total_subjects = conn.execute('SELECT COUNT(*) as count FROM subjects WHERE education_level = ? AND teacher_id = ?', (edu_level, teacher_id)).fetchone()['count']
        total_grades = conn.execute('''SELECT COUNT(*) as count FROM grades g JOIN students s ON g.student_id = s.id WHERE s.education_level = ? AND s.teacher_id = ?''', (edu_level, teacher_id)).fetchone()['count']
        avg_grade = conn.execute('''SELECT AVG(g.final_grade) as avg FROM grades g JOIN students s ON g.student_id = s.id WHERE s.education_level = ? AND s.teacher_id = ?''', (edu_level, teacher_id)).fetchone()['avg'] or 0
        passed = conn.execute('''SELECT COUNT(*) as count FROM grades g JOIN students s ON g.student_id = s.id WHERE s.education_level = ? AND s.teacher_id = ? AND g.final_grade >= 75''', (edu_level, teacher_id)).fetchone()['count']

    stats = {
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_grades': total_grades,
        'avg_grade': avg_grade,
        'passing_rate': 0
    }

    if total_grades > 0:
        stats['passing_rate'] = round((passed / total_grades) * 100, 2)

    conn.close()
    return jsonify(stats)

if __name__ == '__main__':
    # Always initialize/migrate database
    init_db()
    app.run(debug=True)