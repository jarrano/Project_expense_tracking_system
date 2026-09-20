import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"


def add_update_tab():
    selected_date = st.date_input("Enter Date", datetime(2024, 8, 1), label_visibility="collapsed")

    # 1. Fetch data from API
    response = requests.get(f"{API_URL}/expenses/{selected_date}")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    categories = ["Rent", "Food", "Shopping", "Entertainment", "Other"]

    # 2. Update Session State with the newly fetched data
    # This must happen BEFORE the widgets are created inside the form
    for i in range(5):
        if i < len(existing_expenses):
            # If data exists for this row, load it into session state
            st.session_state[f"amount_{i}"] = float(existing_expenses[i]['amount'])
            st.session_state[f"category_{i}"] = existing_expenses[i]["category"]
            st.session_state[f"notes_{i}"] = existing_expenses[i]["notes"]
        else:
            # If no data exists for this row, reset it to defaults
            st.session_state[f"amount_{i}"] = 0.0
            st.session_state[f"category_{i}"] = "Shopping"
            st.session_state[f"notes_{i}"] = ""

    # 3. Build the Form
    with st.form(key="expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text("Amount")
        with col2:
            st.text("Category")
        with col3:
            st.text("Notes")

        expenses = []
        for i in range(5):
            col1, col2, col3 = st.columns(3)

            with col1:
                # Notice: We do NOT use the 'value' parameter anymore.
                # We rely entirely on the key matching the session_state we set above.
                amount_input = st.number_input(
                    label="Amount",
                    min_value=0.0,
                    step=1.0,
                    key=f"amount_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                category_input = st.selectbox(
                    label="Category",
                    options=categories,
                    key=f"category_{i}",
                    label_visibility="collapsed"
                )

            with col3:
                notes_input = st.text_input(
                    label="Notes",
                    key=f"notes_{i}",
                    label_visibility="collapsed"
                )

            expenses.append({
                'amount': amount_input,
                'category': category_input,
                'notes': notes_input
            })

        submit_button = st.form_submit_button()
        if submit_button:
            filtered_expenses = [expense for expense in expenses if expense['amount'] > 0]

            response = requests.post(f"{API_URL}/expenses/{selected_date}", json=filtered_expenses)
            if response.status_code == 200:
                st.success("Expenses updated successfully!")
            else:
                st.error("Failed to update expenses.")