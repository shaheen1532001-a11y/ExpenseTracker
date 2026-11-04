from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB = os.path.join(os.path.dirname(__file__), "expenses.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = get_db()

    transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY id DESC"
    ).fetchall()

    income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type='Income'"
    ).fetchone()[0]

    expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type='Expense'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expenses=expenses,
        balance=income - expenses
    )

@app.route("/add", methods=["POST"])
def add():
    description = request.form["description"].strip()
    amount = float(request.form["amount"])
    transaction_type = request.form["type"]
    category = request.form["category"]

    if not description or amount <= 0:
        return redirect("/")

    if transaction_type not in ["Income", "Expense"]:
        return redirect("/")

    conn = get_db()
    conn.execute(
        "INSERT INTO transactions (description, amount, type, category) VALUES (?, ?, ?, ?)",
        (description, amount, transaction_type, category)
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False) 