import streamlit as st
import requests
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import API_URL

st.set_page_config(
    page_title="Engagement Analytics Platform",
    page_icon="📊",
    layout="wide"
)

if "token" not in st.session_state:
    st.session_state.token = None

if st.session_state.token is None:
    st.title("📊 Engagement Analytics Platform")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
        if submitted:
            try:
                res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password}, timeout=5)
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend.")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            reg_submitted = st.form_submit_button("Register")
        if reg_submitted:
            try:
                res = requests.post(f"{API_URL}/auth/register", json={"username": new_username, "email": new_email, "password": new_password}, timeout=5)
                if res.status_code == 201:
                    st.success("✅ Registered successfully! Please login.")
                else:
                    st.error(res.json().get("detail", "Registration failed."))
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend.")
else:
    st.sidebar.title("📊 Analytics Platform")
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate", ["Overview", "Engagement Trends", "Event Breakdown", "Content Popularity", "ETL Status"])

    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()

    token = st.session_state.token
    headers = {"Authorization": f"Bearer {token}"}

    if page == "Overview":
        from views.overview import show
        show(headers, API_URL)
    elif page == "Engagement Trends":
        from views.trends import show
        show(headers, API_URL)
    elif page == "Event Breakdown":
        from views.events import show
        show(headers, API_URL)
    elif page == "Content Popularity":
        from views.content import show
        show(headers, API_URL)
    elif page == "ETL Status":
        from views.etl_status import show
        show(headers, API_URL)
