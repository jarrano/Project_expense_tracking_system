import streamlit as st
from add_update import add_update_tab
from analytics_by_category import analytics_category_tab
from analytics_by_months import analytics_months_tab


# Optional: Configure the browser tab title and layout
st.set_page_config(page_title="Expense Tracking System", layout="wide")
st.title("Expense Tracking System")

tab1, tab2, tab3 = st.tabs(["Add/Update", "Analytics By Category", "Analytics By Months"])

with tab1:
    add_update_tab()

with tab2:
    analytics_category_tab()

with tab3:
    analytics_months_tab()
# ----------------------