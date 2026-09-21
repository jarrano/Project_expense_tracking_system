# this file will talk with the dababase and retrieve the records called: CRUD
# C - Create
# R - Retrieve
# U - Update
# D - Delete
import logging

import mysql.connector
from contextlib import contextmanager
from backend.logging_setup import setup_logger              # This tells Python: "Go to the project root (which is in the path thanks to conftest), look into the backend folder, and find logging_setup.py."

logger = setup_logger('db_helper')

# ============================================
# 1. DEFINE THE CONNECTION FUNCTION
# ============================================

@contextmanager
def get_db_connection(config):
    """Context manager for database connections"""
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


# ============================================
# 2. DEFINE YOUR CONFIGURATION
# ============================================

production_config = {
    'host': 'localhost',
    'database': 'expense_manager',   # ← Production (used by server.py)
    'user': 'root',
    'password': 'root'
}
test_config = {
    'host': 'localhost',
    'database': 'expense_manager_test', # ← Test (used by test_db_helper.py)
    'user': 'root',
    'password': 'root'
}

# Choose which database to use
config = test_config  # ← Change this to production_config when ready

# ============================================
# 3. DATABASE OPERATIONS FUNCTIONS
# ============================================

# ---------- READ (Select) ----------
def get_all_expenses():
    """Get all expenses"""
    with get_db_connection(config) as cursor:
        cursor.execute("SELECT * FROM expenses ORDER BY expense_date DESC")
        return cursor.fetchall()


def get_expenses_by_date(expense_date):
    logger.info(f'get_expenses_by_date called with: {expense_date}')
    """Get expenses by date"""
    with get_db_connection(config) as cursor:
        query = "SELECT * FROM expenses WHERE expense_date = %s"
        cursor.execute(query, (expense_date,))
        return cursor.fetchall()


def insert_expense(expense_date, amount, category, notes):
    logger.info(f'insert_expense called with date: {expense_date}, amount: {amount}, category: {category}, notes: {notes}')
    """Insert new expense"""
    with get_db_connection(config) as cursor:
        query = "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, params=(expense_date, amount, category, notes,))
        cursor.lastrowid  # ← Store the ID first
        return cursor.lastrowid

    # For INSERT, use lastrowid or rowcount, not fetchall()

def get_expense_summary(start_date, end_date):
    logger.info(f'get_expense_summary called with start: {start_date}, end_date: {end_date}')
    """Get total summary expenses between dates with percentages"""
    with get_db_connection(config) as cursor:
        # Query 1: Category totals
        query_totals = """SELECT category, SUM(amount) AS total
                FROM expenses WHERE expense_date
                BETWEEN %s AND %s
                GROUP BY category
                ORDER BY total DESC;"""
        cursor.execute(query_totals, (start_date, end_date))
        categories = cursor.fetchall()

        if not categories:
            logger.info(f'No expenses found between {start_date} and {end_date}')
            return []

        # Query 2: Grand total
        query_grand_total = """SELECT COALESCE(SUM(amount), 0) AS grand_total              
                FROM expenses WHERE expense_date
                BETWEEN %s AND %s;"""
        cursor.execute(query_grand_total, (start_date, end_date))
        grand_total = cursor.fetchone()["grand_total"]

        # Calculate percentage for each category
        for category in categories:
            if grand_total > 0:
                category["percentage"] = round(
                    (category["total"] / grand_total) * 100, 2
                )
            else:
                category["percentage"] = 0.0

        return categories
# NOTE:
# The triple quotes """...""" define a multi-line string (also called a "triple-quoted string" or "docstring" when used as the first statement in a function).

def get_expense_summary_by_month():
    """Get total summary of expenses grouped by month"""
    with get_db_connection(config) as cursor:
        query_totals_by_month = """
            SELECT 
                MONTHNAME(expense_date) AS month,
                SUM(amount) AS total
            FROM expenses
            GROUP BY 
                YEAR(expense_date),
                MONTH(expense_date),
                MONTHNAME(expense_date)
            ORDER BY 
                YEAR(expense_date),
                MONTH(expense_date);
        """
        cursor.execute(query_totals_by_month)
        by_month = cursor.fetchall()

    # SAFER FORMATTING - Using column names instead of indexes
    if not by_month:
        return []

    formatted_result = []
    for row in by_month:
        formatted_result.append({
            "month": row["month"],
            "total": float(row["total"]) if row["total"] is not None else 0.0
        })

    return formatted_result


def delete_expense(expense_id):
    """Delete an expense by ID"""
    with get_db_connection(config) as cursor:
        query = "DELETE FROM expenses WHERE id = %s"
        cursor.execute(query, (expense_id,))
        return cursor.rowcount  # Returns number of rows deleted

def delete_expense_by_date(expense_date):
    logger.info(f'delete_expense_by_date called with: {expense_date}')
    """Delete an expense by DATE"""
    with get_db_connection(config) as cursor:
        query = "DELETE FROM expenses WHERE expense_date = %s"
        cursor.execute(query, (expense_date,))
        return cursor.rowcount  # Returns number of rows deleted

# ---------- DISPLAY FUNCTIONS ----------
def print_expenses(expenses, title):
    """Print all expenses with a title"""
    if not expenses:
        print(f"📊 {title}: No expenses found")
        return
    print(f"\n📊 {title}:")
    print("-" * 100)
    for expense in expenses:
        print(expense)
    print("-" * 100)



# ============================================
# 4. MAIN EXECUTION (Demo)
# ============================================

if __name__ == "__main__":
    # ----- CREATE -----

    # Get all expenses
    all_expenses = get_all_expenses()
    print_expenses(all_expenses, "ALL EXPENSES")

    # Get expenses by specific date
    aug_expenses = get_expenses_by_date("2024-08-01")
    print_expenses(aug_expenses, "AUGUST EXPENSES")

    # Insert a new expense
    new_id = insert_expense("2024-08-25", 40, "Food", "Eat tasty samosa chat")
    print(f"✅ Inserted expense with ID: {new_id}")

    # Delete an expense (example: delete ID 69)
    expense_id_to_delete = 70
    rows_deleted = delete_expense(expense_id_to_delete)

    if rows_deleted > 0:
        print(f"✅ Successfully deleted expense ID: {expense_id_to_delete}")
    else:
        print(f"❌ Expense ID {expense_id_to_delete} not found")

    # delete expenses by expense_date
    expense_date_to_delete = "2024-08-25"
    rows_deleted = delete_expense_by_date(expense_date_to_delete)

    if rows_deleted > 0:
        print(f"✅ Successfully deleted expense ID: {expense_date_to_delete}")
    else:
        print(f"❌ Expense ID {expense_date_to_delete} not found")

    # Get expenses between dates
    aug_expenses = get_expense_summary("2024-08-01", "2024-08-05")
    print_expenses(aug_expenses, "AUGUST EXPENSES")