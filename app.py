from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.secret_key = "justkeepdebugging"   # you can set any random string


# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",              # change if different
        password="rohit172",  # put your MySQL password
        database="ToDoList"
    )

# ----------------- USER REGISTER -----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except:
            flash("Username already exists!", "danger")
        conn.close()
    return render_template("register.html")

# ----------------- USER LOGIN -----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")

# ----------------- LOGOUT -----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ----------------- CREATE + READ -----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        task_title = request.form["task"]
        cur.execute("INSERT INTO tasks (title, status, user_id) VALUES (%s, %s, %s)",
                    (task_title, "pending", session["user_id"]))
        conn.commit()

    cur.execute("SELECT * FROM tasks WHERE status='pending' AND user_id=%s", (session["user_id"],))
    tasks = cur.fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks, username=session["username"])

# ----------------- UPDATE TASK -----------------
@app.route("/update/<int:task_id>", methods=["GET", "POST"])
def update(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        new_title = request.form["task"]
        cur.execute("UPDATE tasks SET title=%s WHERE id=%s AND user_id=%s",
                    (new_title, task_id, session["user_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    cur.execute("SELECT * FROM tasks WHERE id=%s AND user_id=%s", (task_id, session["user_id"]))
    task = cur.fetchone()
    conn.close()
    return render_template("update.html", task=task)

# ----------------- MARK COMPLETE -----------------
@app.route("/complete/<int:task_id>")
def complete(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='completed' WHERE id=%s AND user_id=%s",
                (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ----------------- COMPLETED TASKS -----------------
@app.route("/completed")
def completed():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE status='completed' AND user_id=%s", (session["user_id"],))
    tasks = cur.fetchall()
    conn.close()
    return render_template("completed.html", tasks=tasks)

# ----------------- DELETE TASK -----------------
@app.route("/delete/<int:task_id>")
def delete(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
