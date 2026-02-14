from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os, random, string
from datetime import datetime

app = Flask(__name__)
app.secret_key = "echo_secret_key"
app.config['UPLOAD_FOLDER'] = "static/uploads"

if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")

# ---------------- DATABASE ----------------

def connect_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        bio TEXT DEFAULT '',
        profile_pic TEXT DEFAULT 'default.png',
        referral_code TEXT,
        points INTEGER DEFAULT 0
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS follows(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        follower_id INTEGER,
        following_id INTEGER,
        status TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        time TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS echoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        content TEXT,
        likes INTEGER DEFAULT 0
    )""")

    conn.commit()
    conn.close()

init_db()

# ---------------- AUTH ----------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        referral=request.form.get("referral")

        conn=connect_db()
        try:
            ref_code=''.join(random.choices(string.ascii_uppercase+string.digits,k=6))
            conn.execute("INSERT INTO users(username,password,referral_code) VALUES(?,?,?)",
                         (username,password,ref_code))

            if referral:
                conn.execute("UPDATE users SET points=points+10 WHERE referral_code=?",(referral,))
            conn.commit()
            return redirect("/")
        except:
            return "Username already exists!"
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():
    username=request.form["username"]
    password=request.form["password"]

    conn=connect_db()
    user=conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                      (username,password)).fetchone()
    conn.close()

    if user:
        session["user_id"]=user["id"]
        session["username"]=user["username"]
        return redirect("/dashboard")
    return "Invalid login"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    search=request.args.get("search")

    conn=connect_db()

    if search:
        users=conn.execute("SELECT * FROM users WHERE username LIKE ? AND id!=?",
                           ("%"+search+"%",session["user_id"])).fetchall()
    else:
        users=conn.execute("SELECT * FROM users WHERE id!=?",
                           (session["user_id"],)).fetchall()

    conn.close()
    return render_template("dashboard.html",users=users)

# ---------------- PROFILE ----------------

@app.route("/profile/<int:user_id>")
def profile(user_id):
    conn=connect_db()
    user=conn.execute("SELECT * FROM users WHERE id=?",(user_id,)).fetchone()

    followers=conn.execute("SELECT COUNT(*) FROM follows WHERE following_id=? AND status='accepted'",
                           (user_id,)).fetchone()[0]
    following=conn.execute("SELECT COUNT(*) FROM follows WHERE follower_id=? AND status='accepted'",
                           (user_id,)).fetchone()[0]

    conn.close()
    return render_template("profile.html",user=user,
                           followers=followers,following=following)

@app.route("/edit_profile",methods=["GET","POST"])
def edit_profile():
    conn=connect_db()

    if request.method=="POST":
        bio=request.form["bio"]
        file=request.files["profile_pic"]

        if file and file.filename!="":
            filename=file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            conn.execute("UPDATE users SET profile_pic=? WHERE id=?",
                         (filename,session["user_id"]))

        conn.execute("UPDATE users SET bio=? WHERE id=?",
                     (bio,session["user_id"]))
        conn.commit()
        conn.close()
        return redirect("/profile/"+str(session["user_id"]))

    user=conn.execute("SELECT * FROM users WHERE id=?",
                      (session["user_id"],)).fetchone()
    conn.close()
    return render_template("edit_profile.html",user=user)

# ---------------- FOLLOW ----------------

@app.route("/follow/<int:user_id>")
def follow(user_id):
    conn=connect_db()
    conn.execute("INSERT INTO follows(follower_id,following_id,status) VALUES(?,?,?)",
                 (session["user_id"],user_id,"pending"))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/notifications")
def notifications():
    conn=connect_db()
    requests=conn.execute("SELECT * FROM follows WHERE following_id=? AND status='pending'",
                          (session["user_id"],)).fetchall()
    conn.close()
    return render_template("notifications.html",requests=requests)

@app.route("/accept/<int:follow_id>")
def accept(follow_id):
    conn=connect_db()
    conn.execute("UPDATE follows SET status='accepted' WHERE id=?",(follow_id,))
    conn.commit()
    conn.close()
    return redirect("/notifications")

# ---------------- CHAT ----------------

@app.route("/chat/<int:user_id>",methods=["GET","POST"])
def chat(user_id):
    conn=connect_db()
    if request.method=="POST":
        msg=request.form["message"]
        conn.execute("INSERT INTO messages(sender_id,receiver_id,message,time) VALUES(?,?,?,?)",
                     (session["user_id"],user_id,msg,str(datetime.now())))
        conn.commit()

    messages=conn.execute("""
        SELECT * FROM messages
        WHERE (sender_id=? AND receiver_id=?)
        OR (sender_id=? AND receiver_id=?)
        ORDER BY id
    """,(session["user_id"],user_id,user_id,session["user_id"])).fetchall()

    conn.close()
    return render_template("chat.html",messages=messages,user_id=user_id)

# ---------------- ECHO ----------------

@app.route("/submit/<int:user_id>",methods=["GET","POST"])
def submit(user_id):
    if request.method=="POST":
        content=request.form["content"]
        conn=connect_db()
        conn.execute("INSERT INTO echoes(sender_id,receiver_id,content) VALUES(?,?,?)",
                     (session["user_id"],user_id,content))
        conn.execute("UPDATE users SET points=points+5 WHERE id=?",
                     (session["user_id"],))
        conn.commit()
        conn.close()
        return redirect("/dashboard")
    return render_template("submit.html")

@app.route("/receive")
def receive():
    conn=connect_db()
    echoes=conn.execute("SELECT * FROM echoes WHERE receiver_id=?",
                        (session["user_id"],)).fetchall()
    conn.close()
    return render_template("receive.html",echoes=echoes)

@app.route("/like_echo/<int:echo_id>")
def like_echo(echo_id):
    conn=connect_db()
    conn.execute("UPDATE echoes SET likes=likes+1 WHERE id=?",(echo_id,))
    conn.commit()
    conn.close()
    return redirect("/receive")

# ---------------- LEADERBOARD ----------------

@app.route("/leaderboard")
def leaderboard():
    conn=connect_db()
    users=conn.execute("SELECT * FROM users ORDER BY points DESC").fetchall()
    conn.close()
    return render_template("leaderboard.html",users=users)

if __name__=="__main__":
    app.run(debug=True)
