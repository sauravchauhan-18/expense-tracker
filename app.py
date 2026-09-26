"""Entry point for the beginner-friendly Expense Tracker application."""

import math
import sqlite3
from datetime import date, datetime
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "instance" / "expenses.db"

app = Flask(__name__)
app.config["DATABASE"] = str(DATABASE_PATH)


def get_db_connection():
    """Open a connection to the app's SQLite database."""
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the transactions table if it does not already exist."""
    connection = get_db_connection()
    schema_path = BASE_DIR / "schema.sql"

    with schema_path.open("r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())

    connection.close()


def validate_transaction_form():
    """Return the cleaned form data, or an error message if it is invalid."""
    transaction_type = request.form.get("type", "").strip()
    amount_text = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    transaction_date = request.form.get("transaction_date", "").strip()

    if transaction_type not in ("income", "expense"):
        return None, "Choose either income or expense."
    if not category:
        return None, "Enter a category."
    if len(category) > 50:
        return None, "Keep the category to 50 characters or fewer."

    try:
        amount = float(amount_text)
    except ValueError:
        return None, "Enter a valid amount."

    if not math.isfinite(amount) or amount <= 0:
        return None, "Amount must be greater than zero."

    try:
        datetime.strptime(transaction_date, "%Y-%m-%d")
    except ValueError:
        return None, "Choose a valid transaction date."

    return {
        "type": transaction_type,
        "amount": amount,
        "category": category,
        "description": description,
        "transaction_date": transaction_date,
    }, None


def find_transaction(transaction_id):
    """Return one transaction, or show a not-found page if it does not exist."""
    connection = get_db_connection()
    transaction = connection.execute(
        "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
    ).fetchone()
    connection.close()

    if transaction is None:
        abort(404)
    return transaction


def get_dashboard_data(category="", start_date="", end_date=""):
    """Read filtered transactions and calculate the current month's totals."""
    current_month = date.today().strftime("%Y-%m")
    connection = get_db_connection()
    query = "SELECT * FROM transactions WHERE 1 = 1"
    query_values = []

    if category:
        query += " AND category = ?"
        query_values.append(category)
    if start_date:
        query += " AND transaction_date >= ?"
        query_values.append(start_date)
    if end_date:
        query += " AND transaction_date <= ?"
        query_values.append(end_date)

    query += " ORDER BY transaction_date DESC, id DESC"
    transactions = connection.execute(query, query_values).fetchall()
    categories = connection.execute(
        "SELECT DISTINCT category FROM transactions ORDER BY category"
    ).fetchall()
    totals = connection.execute(
        """SELECT
               COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
               COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expenses
           FROM transactions
           WHERE strftime('%Y-%m', transaction_date) = ?""",
        (current_month,),
    ).fetchone()
    expense_by_category = connection.execute(
        """SELECT category, SUM(amount) AS total
           FROM transactions
           WHERE type = 'expense' AND strftime('%Y-%m', transaction_date) = ?
           GROUP BY category
           ORDER BY total DESC""",
        (current_month,),
    ).fetchall()
    connection.close()

    return {
        "transactions": transactions,
        "monthly_income": totals["income"],
        "monthly_expenses": totals["expenses"],
        "balance": totals["income"] - totals["expenses"],
        "current_month": date.today().strftime("%B %Y"),
        "expense_by_category": [dict(row) for row in expense_by_category],
        "categories": categories,
        "filter_category": category,
        "filter_start_date": start_date,
        "filter_end_date": end_date,
        "filters_active": bool(category or start_date or end_date),
    }


@app.route("/")
def home():
    """Show the dashboard, entry form, and saved transaction history."""
    category = request.args.get("category", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    for filter_date in (start_date, end_date):
        if filter_date:
            try:
                datetime.strptime(filter_date, "%Y-%m-%d")
            except ValueError:
                return "Please use valid dates in YYYY-MM-DD format.", 400

    dashboard_data = get_dashboard_data(category, start_date, end_date)
    return render_template(
        "index.html",
        **dashboard_data,
        saved=request.args.get("saved") == "1",
        updated=request.args.get("updated") == "1",
        deleted=request.args.get("deleted") == "1",
    )


@app.route("/transactions/add", methods=["POST"])
def add_transaction():
    """Validate the form and save one income or expense transaction."""
    data, error = validate_transaction_form()
    if error:
        return render_template(
            "index.html", **get_dashboard_data(), error=error
        ), 400

    connection = get_db_connection()
    connection.execute(
        """INSERT INTO transactions
           (type, amount, category, description, transaction_date)
           VALUES (?, ?, ?, ?, ?)""",
        (data["type"], data["amount"], data["category"], data["description"], data["transaction_date"]),
    )
    connection.commit()
    connection.close()
    return redirect(url_for("home", saved="1"))


@app.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    """Show the edit form and update an existing transaction."""
    transaction = find_transaction(transaction_id)

    if request.method == "POST":
        data, error = validate_transaction_form()
        if error:
            return render_template(
                "transaction_form.html", transaction=transaction, error=error
            ), 400

        connection = get_db_connection()
        connection.execute(
            """UPDATE transactions
               SET type = ?, amount = ?, category = ?, description = ?, transaction_date = ?
               WHERE id = ?""",
            (data["type"], data["amount"], data["category"], data["description"],
             data["transaction_date"], transaction_id),
        )
        connection.commit()
        connection.close()
        return redirect(url_for("home", updated="1"))

    return render_template("transaction_form.html", transaction=transaction)


@app.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
def delete_transaction(transaction_id):
    """Delete one transaction from the database."""
    find_transaction(transaction_id)
    connection = get_db_connection()
    connection.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    connection.commit()
    connection.close()
    return redirect(url_for("home", deleted="1"))


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
