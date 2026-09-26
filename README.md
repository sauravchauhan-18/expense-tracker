# Expense Tracker & Analytics Dashboard

A small personal finance web application built as a CSE college project. It lets a user record income and expenses, review transactions, and see a summary and charts for the current month.

## Features

- Add income and expense transactions with an amount, category, date, and optional description.
- Validate the transaction type, positive amount, category, and date before saving.
- View transaction history, ordered by date with the newest entries first.
- Edit or delete a transaction.
- Filter transaction history by category and an inclusive start and end date.
- View current calendar month's income, expenses, and remaining balance.
- View a chart comparing monthly income and expenses and a chart of monthly expenses by category.

The monthly summary and charts use all transactions in the current month. The category and date filters affect the history list only.

## Technologies

- Python
- Flask
- SQLite through Python's built-in `sqlite3` module
- HTML
- CSS
- Vanilla JavaScript and the browser's Canvas API for charts

## Project structure

```text
expense-tracker/
├── app.py                       # Flask routes, validation, and database queries
├── schema.sql                   # SQLite transactions table definition
├── requirements.txt             # Python package requirements
├── README.md                    # Project documentation
├── .gitignore                   # Files Git should leave out
├── instance/
│   ├── .gitkeep                 # Keeps this folder in Git
│   └── expenses.db              # Created when the app first runs; ignored by Git
├── templates/
│   ├── index.html               # Dashboard, add form, summary, and history
│   └── transaction_form.html    # Edit transaction form
└── static/
    ├── css/
    │   └── style.css            # Page styling
    └── js/
        └── main.js              # Canvas chart drawing
```

The `.venv/` folder is created on your computer when you make a Python virtual environment. It is ignored by Git and is not part of the project source files.

## Database

The app uses one SQLite table named `transactions`. The database file is `instance/expenses.db`. When you run `app.py`, the app creates the `instance` folder if needed and runs `schema.sql` to create the table if it does not already exist.

| Column | Description |
| --- | --- |
| `id` | Unique transaction ID |
| `type` | `income` or `expense` |
| `amount` | Transaction amount |
| `category` | Category entered by the user, stored as text |
| `description` | Optional note |
| `transaction_date` | Transaction date in `YYYY-MM-DD` format |
| `created_at` | Time the row was created, set by SQLite |

Categories are stored directly as text in each transaction; there is no separate categories table.

## Install dependencies

Open PowerShell in the project folder. On Windows, create a virtual environment and install Flask with:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` contains Flask. SQLite support comes with Python, so it does not need a separate install.

## Run the Flask application

From the project folder, run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in a browser. Keep the terminal open while using the app. Press **Ctrl+C** in the terminal to stop it.

## Use the application

1. Select **Income** or **Expense**.
2. Enter a positive amount, category, and date. A description is optional.
3. Select **Save transaction**. The entry appears in the transaction history.
4. Use **Edit** to change an entry or **Delete** to remove it.
5. Use the category and date fields above the history to filter the list. Select **Clear filters** to show all entries again.
6. The summary and charts show data for the current calendar month.

## Possible future improvements

- Let the user choose which month to summarize.
- Add CSV export for transaction history.
- Add automated tests for validation and database operations.
- Add pagination when the transaction list becomes long.
