from fastapi import FastAPI, HTTPException
from datetime import date
from backend import db_helper
from typing import List
from pydantic import BaseModel

app = FastAPI()          # create app object

class Expense(BaseModel):
    # expense_date: date    # already I don't needed because in Postman I have the search with the date http://127.0.0.1:8000/expenses/2024-08-01
    amount: float
    category: str
    notes: str

class DateRange(BaseModel):
    start_date: date
    end_date: date


# when you retrieve records we use GET Method, if you are passing complex object we use POST Method
# example: GET : http://127.0.0.1:8000/expenses/2024-08-01

@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expense(expense_date: date):
    expenses = db_helper.get_expenses_by_date(expense_date)
    return expenses

# now I run the command uvicorn that FastAPI runs internally: uvicorn server:app--reload


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expense]):
    # 1. Delete existing expenses for this date
    db_helper.delete_expense_by_date(expense_date)

    # 2. Insert each expense
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)

    # 3. Return success
    return {"message": f"{len(expenses)} expense(s) added successfully!"}

@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.get_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from database")
    return data

@app.get("/analytics_by_month/")
def get_analytics_by_month():
    data = db_helper.get_expense_summary_by_month()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve monthly summary")
    return data
