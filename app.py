from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = '0000'

# Configure Gemini API
genai.configure(api_key="AIzaSyCviYMhPq10IHqxKmBUQxrPZuff7Ki-9LU")
model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize the database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Registration route
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        hashed_password = generate_password_hash(raw_password)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another.')
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_hash = result[0]
            if check_password_hash(stored_hash, password):
                flash('Login successful!')
                session['username'] = username
                return redirect(url_for('chat'))
            else:
                flash('Incorrect password.')
                return redirect(url_for('login'))
        else:
            flash('User not found.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Chat route
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        flash("Please login first.")
        return redirect(url_for('login'))

    user_message = ''
    bot_reply = ''

    if request.method == 'POST':
        user_message = request.form['message']
        try:
            response = model.generate_content(user_message)
            bot_reply = response.text
        except Exception as e:
            bot_reply = "Error talking to Gemini: " + str(e)

    return render_template('chat.html', user_message=user_message, bot_reply=bot_reply)

# Run the app
if __name__ == '__main__':
    print("Starting Flask app...")
    init_db()
    app.run(debug=True)