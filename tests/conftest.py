# The name "conftest" stands for "CONFIGURATION FOR TESTS"
# conftest.py is doing path configuration - it's adding your project root to Python's path so imports work correctly:


import os
import sys
# Gets the directory where conftest.py is located (tests/backend/)
# Then goes up one level (..) to reach project root

project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)          # ← path must be set up FIRST
print(sys.path)

import pytest                              # ← pytest doesn't depend on path, fine anywhere
from backend import db_helper              # ← THIS must come AFTER sys.path.insert

def pytest_configure(config):
    """
    Pytest calls this automatically once, before any test runs.
    We swap db_helper's `config` variable so every CRUD function
    (which reads `config` by name) points at expense_manager_test
    instead of the real expense_manager database.
    """
    db_helper.config = db_helper.test_config
    print(f"✅ Tests will run against: {db_helper.config['database']}")


@pytest.fixture
def my_value():
    return 100

###########################################################################################################################
@pytest.fixture
def expense_snapshot(request):
    test_date = request.param
    saved_expenses = db_helper.get_expenses_by_date(test_date)   # ① runs first, 📸 PHOTO #1 — BEFORE anything happens

    yield test_date, saved_expenses    # ② PAUSES here, hands data over, ⏸️ test runs now — it calls delete_expense_by_date()

    # ④ execution resumes here, AFTER the test finishes
    remaining = db_helper.get_expenses_by_date(test_date) # 📸 PHOTO #2 — AFTER the test deleted stuff
    remaining_ids = {e["id"] for e in remaining}
    for exp in saved_expenses:
        if exp["id"] not in remaining_ids:
            db_helper.insert_expense(
                expense_date=exp["expense_date"],
                amount=exp["amount"],
                category=exp["category"],
                notes=exp["notes"],
            )

@pytest.fixture
def new_expense():              # ← empty parentheses, no "request" parameter — nothing is being fed in from outside
    new_id = db_helper.insert_expense(
        expense_date="2024-10-01",
        amount=30.00,
        category="Food",
        notes="Coffee beans",
    )

    yield new_id

    db_helper.delete_expense(new_id)




# What this does:
# os.path.dirname(__file__) → C:/code/Project_expense_tracking_system/tests/backend
#
# os.path.join(..., "..") → C:/code/Project_expense_tracking_system (project root)
#
# sys.path.insert(0, project_root) → Allows from backend import db_helper to work


# Project_expense_tracking_system/
# │
# ├── backend/
# │   ├── __init__.py          ← IMPORTANT: Makes it a package
# │   └── db_helper.py
# │
# ├── tests/
# │   └── backend/
# │       ├── __init__.py      ← IMPORTANT: Makes it a package
# │       └── test_db_helper.py
# │
# ├── conftest.py              ← Your path configuration
# └── venv/

# ============================================
# DATABASE OVERRIDE FOR TESTS
# ============================================
# This must run AFTER the sys.path setup above, because it needs to
# import db_helper — and that import only works once project_root
# has been added to sys.path.