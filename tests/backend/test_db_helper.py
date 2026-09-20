import mysql.connector
from contextlib import contextmanager
from backend.logging_setup import setup_logger


def test_get_expenses_by_date():
   expenses = db_helper.get_expenses_by_date("2024-08-15")

   assert len(expenses) == 1                       # 1 (because there's 1 record); # 1 == 1 ✅ TRUE - Test passes!
   assert expenses[0]["amount"] == 10.0
   assert expenses[0]["category"] == "Shopping"
   assert expenses[0]["notes"] == "Bought potatoes"


def test_get_expenses_by_date_invalid_date():
   expenses = db_helper.get_expenses_by_date("9999-08-15")

   assert len(expenses) == 0

# Note:
# if len(expenses) == 0, Result: The test would PASS (because len(expenses) is 0).
# if len(expenses) == 1, Result: The test would FAIL (because len(expenses) is 0, but you expected 1).


def test_get_expense_summary_invalid_range():
   summary = db_helper.get_expense_summary("2099-01-01", "2099-12-31")
   assert len(summary) == 0           # should be 0 because I am doing a wrong range


# def test_insert_expense():
#    """Test inserting a new expense - with guaranteed cleanup"""
#    new_id = None
#    try:
#       # ----- INSERT test data -----
#       new_id = db_helper.insert_expense(
#          expense_date="2024-08-20",
#          amount=25.50,
#          category="Transport",
#          notes="Monthly MRT pass"
#       )
#
#       # ----- VERIFY it was inserted -----
#       expenses = db_helper.get_expenses_by_date("2024-08-20")
#
#       # ----- ASSERTIONS -----
#       assert len(expenses) == 1
#       assert expenses[0]["id"] == new_id
#       assert expenses[0]["amount"] == 25.50
#       assert expenses[0]["category"] == "Transport"
#       assert expenses[0]["notes"] == "Monthly MRT pass"
#
#    finally:
#       # ----- CLEANUP (ALWAYS runs) -----
#       if new_id:
#          db_helper.delete_expense(new_id)
#          print(f"✅ Cleaned up expense ID: {new_id}")

##################################################################################
# def test_delete_expense_by_date_multiple():
#    """Test deleting expenses by DATE when there are multiple expenses - with restoration"""
#    test_date = "2024-08-02"
#    expenses_before = db_helper.get_expenses_by_date(test_date)
#
#    if not expenses_before:
#       print(f'No expenses found for {test_date} - skipping test')
#       return
#
#    # Save a copy of ALL data for restoration
#    saved_expenses = []
#    for exp in expenses_before:
#       saved_expenses.append({
#          'id': exp["id"],
#          'expense_date': exp["expense_date"],
#          'amount': exp["amount"],
#          'category': exp["category"],
#          'notes': exp["notes"]
#       })
#
#    print(f'📋 Found {len(saved_expenses)} expenses for {test_date}')
#    for exp in saved_expenses:
#       # ✅ FIXED: Added quotes around 'id'
#       print(f"   ID: {exp['id']}, Amount: {exp['amount']}, Category: {exp['category']}")
#
#    try:
#       rows_deleted = db_helper.delete_expense_by_date(test_date)
#       print(f'🗑️ Deleted {rows_deleted} expenses for {test_date}')
#
#       # Step 3: VERIFY ALL are gone
#       expenses_after = db_helper.get_expenses_by_date(test_date)
#       assert len(expenses_after) == 0
#       assert rows_deleted == len(expenses_before)  # All rows deleted
#
#    finally:
#       # Step 4: RESTORE ALL (ALWAYS runs)
#       for exp in saved_expenses:
#          db_helper.insert_expense(
#             expense_date=exp["expense_date"],
#             amount=exp["amount"],  # ✅ FIXED: Added quotes
#             category=exp["category"],
#             notes=exp["notes"]
#          )
#       # ✅ FIXED: This is now INSIDE the finally block (indented)
#       print(f"♻️ Restored {len(saved_expenses)} expense(s) for {test_date}")

@pytest.mark.parametrize("expense_snapshot", ["2024-08-15"], indirect=True)
def test_delete_expense_by_date_multiple(expense_snapshot):
   test_date, saved_expenses = expense_snapshot  # ③ receives what yield sent

   rows_deleted = db_helper.delete_expense_by_date(test_date)  # ③ delete happens HERE, in the test
   expenses_after = db_helper.get_expenses_by_date(test_date)

   assert len(expenses_after) == 0
   assert rows_deleted == len(saved_expenses)
   # ← once this function ends, control goes back to step ④ in the fixture


##################################################################################
def test_insert_expense(new_expense):              # new_expense is the name of the fixture itself (it is the helper name function's name), new_expense a special case: pytest sees that name, recognizes it as a fixture's name, runs the fixture, and drops the result into that slot for you.

      expenses = db_helper.get_expenses_by_date("2024-10-01")          # is a plain function call, straight from test_db_helper.py to db_helper.py

      # ----- ASSERTIONS -----
      assert len(expenses) == 1
      assert expenses[0]["id"] == new_expense
      assert expenses[0]["amount"] == 30.00
      assert expenses[0]["category"] == "Food"
      assert expenses[0]["notes"] == "Coffee beans"


##################################################################################
# IMPORTANT:
# Running pytest from the Project Root is the standard and best practice for this type of project structure because it makes Python's path resolution much simpler.
# Example: from the project root directory run : pytest -v -s tests/backend/test_db_helper.py::test_insert_expense

# 💡 Note on your working directory
# It is generally much easier to run tests from the Project Root (the folder containing backend and tests), rather than moving into the tests folder itself.
##################################################################################




# Note1:
# assert is a statement that checks if a condition is True. If it's True, the test passes. If it's False, the test fails and raises an AssertionError.
# 1. Check HOW MANY records were returned
# assert len(expenses) == 1  # ← "I expect exactly 1 expense"
#
# 2. Check the data in the first record
# assert expenses[0]["amount"] == 10.0  # ← "I expect amount to be 10.0"
# assert expenses[0]["category"] == "Shopping"  # ← "I expect category to be 'Shopping'"
# assert expenses[0]["notes"] == "Bought potatoes"  # ← "I expect notes to match"


# Note2
# ❌ WRONG: Cleanup only runs if test passes
# def test_insert():
#     new_id = insert(...)
#     assert ...  # ← If this fails, cleanup never runs!
#     delete(new_id)
#
# ✅ CORRECT: Cleanup ALWAYS runs (even on failure)
# def test_insert():
#     new_id = None
#     try:
#         new_id = insert(...)
#         assert ...
#     finally:
#         if new_id:
#             delete(new_id)  # ← ALWAYS runs!

