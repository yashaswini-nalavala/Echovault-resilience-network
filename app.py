from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "echovault_secret_key"


# -------------------------------
# DATABASE SETUP
# -------------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Echoes table
    c.execute("""
        CREATE TABLE IF NOT EXISTS echoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            emotion TEXT,
            message TEXT
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------------
# REGISTER
# -------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Username already exists. Try another."

    return render_template("register.html")


# -------------------------------
# LOGIN
# -------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")


# -------------------------------
# LOGOUT
# -------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------------------
# DASHBOARD
# -------------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # User echo count
    c.execute("SELECT COUNT(*) FROM echoes WHERE user_id=?",
              (session["user_id"],))
    total_echoes = c.fetchone()[0]

    # Global stats
    c.execute("SELECT emotion, COUNT(*) FROM echoes GROUP BY emotion")
    stats = c.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           total_echoes=total_echoes,
                           stats=stats)


# -------------------------------
# SUBMIT ECHO
# -------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
        return redirect("/login")

    emotion = request.form["emotion"]
    message = request.form["message"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO echoes (user_id, emotion, message) VALUES (?, ?, ?)",
              (session["user_id"], emotion, message))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -------------------------------
# RECEIVE ECHO
# -------------------------------
@app.route("/receive", methods=["GET", "POST"])
def receive():
    if "user_id" not in session:
        return redirect("/login")

    echo = None

    if request.method == "POST":
        emotion = request.form["emotion"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT message FROM echoes WHERE emotion=?", (emotion,))
        results = c.fetchall()
        conn.close()

        if results:
            echo = random.choice(results)[0]
        else:
            echo = "No echoes yet. Be the first to leave hope."

    return render_template("receive.html", echo=echo)


# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
