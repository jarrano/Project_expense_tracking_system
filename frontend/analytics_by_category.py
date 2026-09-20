import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL = 'http://localhost:8000'

def analytics_category_tab():
    st.subheader("Expense Analytics")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime(2024, 8, 1))
    with col2:
        end_date = st.date_input("End Date", datetime(2024, 8, 5))

    if st.button("Get Analytics", type="primary"):
        try:
            payload = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            response = requests.post(f"{API_URL}/analytics/", json=payload)

            if response.status_code == 200:
                data = response.json()

                if not data:
                    st.warning("No expenses found for this date range.")
                    return

                formatted_data = {
                    "Category": [item["category"] for item in data],
                    "Total": [item["total"] for item in data],
                    "Percentage": [item["percentage"] for item in data]
                }

                df = pd.DataFrame(formatted_data)
                df_sorted = df.sort_values(by="Percentage", ascending=False)

                st.title("Expense Breakdown By Category")

                st.bar_chart(
                    data=df_sorted.set_index("Category")['Percentage'],
                    use_container_width=True
                )

                df_sorted["Total"] = df_sorted["Total"].map("{:.2f}".format)
                df_sorted["Percentage"] = df_sorted["Percentage"].map("{:.2f}".format)

                st.table(df_sorted)

            else:
                st.error(f"Failed to fetch analytics data. Status code: {response.status_code}")
                st.write("**FastAPI Error Details:**")
                st.json(response.json())

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend server. Is Uvicorn running?")