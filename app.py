from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os

# ======================= 🔹 Flask App Configuration 🔹 =======================
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
app.secret_key = 'your_secret_key_here'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ======================= 🔹 MySQL Configuration 🔹 =======================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '@priti123'
app.config['MYSQL_DB'] = 'quiz_portal'
mysql = MySQL(app)

# ======================= 🔹 Flask-Mail Configuration 🔹 =======================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jpriti5462@gmail.com'  # ✅ your Gmail
app.config['MAIL_PASSWORD'] = 'xcxgqaqktolqhdcj'      # ✅ App password
app.config['MAIL_DEFAULT_SENDER'] = 'jpriti5462@gmail.com'  # ✅ same sender
mail = Mail(app)

# ============================================================================

# 🏠 Home / Login system routes
@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            flash('Email already exists! Please login.', 'warning')
            return redirect(url_for('login'))
        else:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                           (username, email, password))
            mysql.connection.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')
    return render_template("login.html")

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    else:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('loggedin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ============================================================================

# 🧩 About / Fun / Learn Pages
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/fun')
def fun():
    if 'loggedin' in session:
        return render_template('fun.html')
    flash('Please login to access the fun page!', 'warning')
    return redirect(url_for('login'))

@app.route('/learn')
def learn():
    return render_template('learn.html')

# ============================================================================

# 💬 Contact Page (Mail)
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        msg = Message(
            subject=f"📩 New Contact Message: {subject}",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=['jpriti5462@gmail.com'],
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        )

        try:
            mail.send(msg)
            flash('✅ Message sent successfully! Thank you for contacting us.', 'success')
        except Exception as e:
            flash(f'❌ Failed to send email: {str(e)}', 'danger')
    return render_template('contact.html')

# ============================================================================

# 🎯 Levels Page
@app.route('/level')
def levels():
    if 'loggedin' in session:
        return render_template('levels.html')
    else:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

# ============================================================================


@app.route('/quiz/<level>')
def quiz(level):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM questions WHERE level = %s", (level,))
    questions = cursor.fetchall()
    return render_template('quiz.html', questions=questions, level=level)


@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    level = request.form.get('level', 'Easy')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM questions WHERE level = %s", (level,))
    questions = cursor.fetchall()

    score = 0
    total = len(questions)

    for q in questions:
        qid = str(q['id'])
        user_answer = request.form.get(qid)
        if user_answer == q['correct_option']:
            score += 1

    return render_template('result.html', score=score, total=total, level=level)

# ============================================================================

# 🚀 Run App
if __name__ == '__main__':
    app.run(debug=True)
