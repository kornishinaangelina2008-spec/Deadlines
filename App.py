from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "deadlines.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deadlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            task TEXT NOT NULL,
            due_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM deadlines ORDER BY due_date ASC"
    ).fetchall()
    conn.close()

    today = datetime.now().date()
    items = []
    for r in rows:
        due = datetime.strptime(r["due_date"], "%Y-%m-%d").date()
        days_left = (due - today).days
        items.append({
            "id": r["id"],
            "subject": r["subject"],
            "task": r["task"],
            "due_date": r["due_date"],
            "days_left": days_left,
            "overdue": days_left < 0,
        })
    return render_template("index.html", items=items)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        subject = request.form["subject"].strip()
        task = request.form["task"].strip()
        due_date = request.form["due_date"]

        if subject and task and due_date:
            conn = get_db()
            conn.execute(
                "INSERT INTO deadlines (subject, task, due_date, created_at) VALUES (?, ?, ?, ?)",
                (subject, task, due_date, datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/delete/<int:item_id>")
def delete(item_id):
    conn = get_db()
    conn.execute("DELETE FROM deadlines WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))
init_db()

