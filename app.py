from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "finance.db"


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)

    db.commit()
    db.close()


@app.route("/")
def index():
    db = get_db()

    transactions = db.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
    """).fetchall()

    income = db.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'income'
    """).fetchone()[0]

    expense = db.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'expense'
    """).fetchone()[0]

    count = db.execute("""
        SELECT COUNT(*)
        FROM transactions
    """).fetchone()[0]

    balance = income - expense

    db.close()

    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expense=expense,
        balance=balance,
        count=count
    )


@app.route("/add", methods=["POST"])
def add_transaction():
    title = request.form.get("title", "").strip()
    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    transaction_type = request.form.get("type", "").strip()
    note = request.form.get("note", "").strip()

    if not title or not amount or not category:
        return redirect(url_for("index"))

    try:
        amount = float(amount)
    except ValueError:
        return redirect(url_for("index"))

    if amount <= 0:
        return redirect(url_for("index"))

    if transaction_type not in ("income", "expense"):
        return redirect(url_for("index"))

    db = get_db()

    db.execute("""
        INSERT INTO transactions (
            title,
            amount,
            category,
            type,
            note,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        amount,
        category,
        transaction_type,
        note,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    db.commit()
    db.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    db = get_db()

    db.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    db.commit()
    db.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:transaction_id>", methods=["POST"])
def edit_transaction(transaction_id):
    title = request.form.get("title", "").strip()
    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    transaction_type = request.form.get("type", "").strip()
    note = request.form.get("note", "").strip()

    if not title or not amount or not category:
        return redirect(url_for("index"))

    try:
        amount = float(amount)
    except ValueError:
        return redirect(url_for("index"))

    if amount <= 0:
        return redirect(url_for("index"))

    if transaction_type not in ("income", "expense"):
        return redirect(url_for("index"))

    db = get_db()

    db.execute("""
        UPDATE transactions
        SET
            title = ?,
            amount = ?,
            category = ?,
            type = ?,
            note = ?
        WHERE id = ?
    """, (
        title,
        amount,
        category,
        transaction_type,
        note,
        transaction_id
    ))

    db.commit()
    db.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
