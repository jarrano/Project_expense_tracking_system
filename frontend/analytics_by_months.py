import streamlit as st
import requests
import pandas as pd

API_URL = 'http://localhost:8000'


def analytics_months_tab():
    st.subheader("Monthly Expense Analytics")

    if st.button("Get Monthly Analytics", type="primary"):
        try:
            response = requests.get(f"{API_URL}/analytics_by_month/")

            if response.status_code == 200:
                data = response.json()

                if not data:
                    st.warning("No expenses found in the database.")
                    return

                # 1. Convert list of dicts to DataFrame
                # The keys are 'month' and 'total' (lowercase)
                df = pd.DataFrame(data)

                st.title("Expense Breakdown By Month")

                # 2. Bar Chart - Use lowercase "month"
                # (We can use the index of the DataFrame, which follows SQL order)
                st.bar_chart(
                    data=df.set_index("month")["total"],
                    use_container_width=True,
                    sort=False  # <-- This tells Streamlit "do NOT sort alphabetically, use my SQL order"
                )

                # 3. Format the Table
                df_display = df.copy()
                df_display["total"] = df_display["total"].map("${:,.2f}".format)

                # Optional: Rename columns to look nicer in the table
                df_display = df_display.rename(columns={"month": "Month", "total": "Total"})

                st.table(df_display)

            else:
                st.error(f"Failed to fetch analytics data. Status code: {response.status_code}")
                st.write("**FastAPI Error Details:**")
                st.text(response.text)

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend server. Is Uvicorn running?")