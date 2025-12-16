import streamlit as st
import pandas as pd
import sqlite3
import hashlib

st.set_page_config(page_title="Cyber Intelligence Dashboard", layout="wide")


#Hasing the Password
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

#Database Setup
def get_connection():
    return sqlite3.connect("app/data/intelligence_platform.db", check_same_thread=False)


def create_users_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()


create_users_table()


#Session State of the user:
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

#Login Page
def login_page():
    st.title("Login to Cyber Intelligence Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        query = "SELECT * FROM users WHERE username = ?"
        user = conn.execute(query, (username,)).fetchone()
        conn.close()

        if user and user[2] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")


#The Registration Page
def registration_page():
    st.title("Create A New Account:")

    new_user = st.text_input("Choose a Username")
    new_pass = st.text_input("Choose a Password", type="password")

    if st.button("Register"):
        if len(new_pass) < 4:
            st.error("Password must be at least 4 characters.")
            return

        conn = get_connection()

        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (new_user, hash_password(new_pass), "user")
            )
            conn.commit()
            st.success("Account created successfully! You can now log in.")
        except:
            st.error("❌ Username already exists")

        conn.close()


# ----------------------------------------
# SHOW LOGIN OR REGISTER
# ----------------------------------------
if not st.session_state.logged_in:
    menu = st.sidebar.radio("Select Page", ["Login", "Register"])

    if menu == "Login":
        login_page()
    else:
        registration_page()

    st.stop()


# ----------------------------------------
# DASHBOARD (ONLY AFTER LOGIN)
# ----------------------------------------
st.title("🔍 Cyber Intelligence Dashboard")
st.write(f"Welcome, **{st.session_state.current_user}** 👋")

# Connect to DB
conn = get_connection()

# Sidebar Navigation
page = st.sidebar.selectbox("Navigation", ["Users", "Cyber Incidents", "Datasets", "Tickets"])


# ----------------------------------------
# USERS PAGE
# ----------------------------------------
if page == "Users":
    st.header("👤 Users Table")
    df = pd.read_sql_query("SELECT * FROM users;", conn)
    st.dataframe(df)


# ----------------------------------------
# CYBER INCIDENTS PAGE
# ----------------------------------------
elif page == "Cyber Incidents":
    st.header("⚠️ Cyber Incidents")

    df = pd.read_sql_query("SELECT * FROM cyber_incidents;", conn)

    # Filtering dropdowns
    severity_filter = st.selectbox("Filter by Severity", ["All", "Low", "Medium", "High", "Critical"])
    category_filter = st.selectbox("Filter by Category", ["All", "Phishing", "DDOS", "Malware", "Misconfiguration", "Unauthorized Access"])
    status_filter = st.selectbox("Filter by Status", ["All", "Resolved", "Open", "Waiting for User", "In Progress"])

    # Apply filters
    if severity_filter != "All":
        df = df[df["severity"] == severity_filter]

    if category_filter != "All":
        df = df[df["category"] == category_filter]

    if status_filter != "All":
        df = df[df["status"] == status_filter]

    st.dataframe(df)


# ----------------------------------------
# DATASETS PAGE
# ----------------------------------------
elif page == "Datasets":
    st.header("📁 Datasets Metadata")
    df = pd.read_sql_query("SELECT * FROM datasets_metadata;", conn)
    st.dataframe(df)


# ----------------------------------------
# TICKETS PAGE
# ----------------------------------------
elif page == "Tickets":
    st.header("🎫 IT Tickets")
    df = pd.read_sql_query("SELECT * FROM it_tickets;", conn)

    status_filter = st.selectbox(
        "Filter Tickets by Status",
        ["All", "Resolved", "Open", "Waiting for User", "In Progress"]
    )

    if status_filter != "All":
        df = df[df["status"] == status_filter]

    st.dataframe(df)


conn.close()
