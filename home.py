import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

st.set_page_config(page_title="Cyber Intelligence Dashboard", layout="wide")

#LOGIN DETAILS
VALID_USERNAME = "Olaf"
VALID_PASSWORD = "admin123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login_page():
    st.title("Login to Cyber Intelligence Dashboard")
    st.write("Enter your credentials to continue.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password.")


if not st.session_state.logged_in:
    login_page()
    st.stop()

# DB HELPERS
DB_PATH = "app/data/intelligence_platform.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def load_df(query: str) -> pd.DataFrame:
    conn = get_conn()
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def pie_chart(count_df: pd.DataFrame, label_col: str, value_col: str, title: str):
    # Altair pie chart
    chart = (
        alt.Chart(count_df)
        .mark_arc()
        .encode(
            theta=alt.Theta(field=value_col, type="quantitative"),
            color=alt.Color(field=label_col, type="nominal"),
            tooltip=[label_col, value_col],
        )
        .properties(title=title, height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def line_chart(time_df: pd.DataFrame, time_col: str, value_col: str, title: str):
    chart = (
        alt.Chart(time_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(time_col + ":T", title="Date"),
            y=alt.Y(value_col + ":Q", title="Count"),
            tooltip=[time_col, value_col],
        )
        .properties(title=title, height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def safe_to_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


# DASHBOARD
st.title("Cyber Intelligence Dashboard")
st.caption("Streamlit dashboard pulling data from SQLite")

page = st.sidebar.selectbox("Navigation", ["Users", "Cyber Incidents", "Datasets", "Tickets"])

# USERS
if page == "Users":
    st.header("Users Table")

    df = load_df("SELECT * FROM users;")
    st.dataframe(df, use_container_width=True)

    st.subheader("Users by Role (Pie)")
    if "role" in df.columns and not df.empty:
        role_count = df["role"].fillna("Unknown").value_counts().reset_index()
        role_count.columns = ["role", "count"]
        pie_chart(role_count, "role", "count", "Users by Role")
    else:
        st.info("No 'role' column found (or table is empty), so no pie chart.")

    st.subheader("Cumulative Users (Line)")
    if "id" in df.columns and not df.empty:
        tmp = df[["id"]].copy()
        tmp["id"] = pd.to_numeric(tmp["id"], errors="coerce")
        tmp = tmp.dropna().sort_values("id")
        # Fake a cumulative line by id order (since there’s no created_date for users)
        tmp["date"] = pd.date_range("2024-01-01", periods=len(tmp), freq="D")
        tmp["count"] = range(1, len(tmp) + 1)
        line_chart(tmp[["date", "count"]], "date", "count", "Cumulative Users (proxy)")
        st.caption("Note: users table has no created_date, so this is a simple proxy trend.")
    else:
        st.info("No 'id' column found (or table is empty), so no line chart.")


# CYBER INCIDENTS
elif page == "Cyber Incidents":
    st.header("Cyber Incidents")

    df = load_df("SELECT * FROM cyber_incidents;")

    # Filters (dropdowns)
    st.subheader("Filters")
    colA, colB, colC = st.columns(3)

    sev_options = ["All", "Low", "Medium", "High", "Critical"]
    cat_options = ["All", "Phishing", "DDoS", "Malware", "Misconfiguration", "Unauthorized Access"]
    status_options = ["All", "Resolved", "Open", "Waiting for User", "In Progress", "Closed"]

    severity = colA.selectbox("Severity", sev_options)
    category = colB.selectbox("Category", cat_options)
    status = colC.selectbox("Status", status_options)

    f = df.copy()
    if severity != "All" and "severity" in f.columns:
        f = f[f["severity"] == severity]
    if category != "All" and "category" in f.columns:
        f = f[f["category"] == category]
    if status != "All" and "status" in f.columns:
        f = f[f["status"] == status]

    st.dataframe(f, use_container_width=True)

    st.subheader("Severity Distribution (Pie)")
    if "severity" in f.columns and not f.empty:
        sev_count = f["severity"].fillna("Unknown").value_counts().reset_index()
        sev_count.columns = ["severity", "count"]
        pie_chart(sev_count, "severity", "count", "Incident Severity Breakdown")
    else:
        st.info("No data for severity pie chart (after filtering).")

    st.subheader("Incidents Over Time (Line)")
    if "timestamp" in f.columns and not f.empty:
        tmp = f.copy()
        tmp["timestamp"] = safe_to_datetime(tmp["timestamp"])
        tmp = tmp.dropna(subset=["timestamp"])
        if tmp.empty:
            st.info("No valid timestamps to chart.")
        else:
            tmp["date"] = tmp["timestamp"].dt.date
            daily = tmp.groupby("date").size().reset_index(name="count")
            daily["date"] = pd.to_datetime(daily["date"])
            line_chart(daily, "date", "count", "Incidents per Day")
    else:
        st.info("No 'timestamp' column found (or no data after filtering).")


# DATASETS
elif page == "Datasets":
    st.header("Datasets Metadata")

    df = load_df("SELECT * FROM datasets_metadata;")
    st.dataframe(df, use_container_width=True)

    st.subheader("Uploads by User (Pie)")
    if "uploaded_by" in df.columns and not df.empty:
        uploader_count = df["uploaded_by"].fillna("Unknown").value_counts().reset_index()
        uploader_count.columns = ["uploaded_by", "count"]
        pie_chart(uploader_count, "uploaded_by", "count", "Datasets Uploaded by User")
    else:
        st.info("No 'uploaded_by' column found (or table is empty).")

    st.subheader("Uploads Over Time (Line)")
    if "upload_date" in df.columns and not df.empty:
        tmp = df.copy()
        tmp["upload_date"] = safe_to_datetime(tmp["upload_date"])
        tmp = tmp.dropna(subset=["upload_date"])
        if tmp.empty:
            st.info("No valid upload_date values to chart.")
        else:
            tmp["date"] = tmp["upload_date"].dt.date
            daily = tmp.groupby("date").size().reset_index(name="count")
            daily["date"] = pd.to_datetime(daily["date"])
            line_chart(daily, "date", "count", "Dataset Uploads per Day")
    else:
        st.info("No 'upload_date' column found (or table is empty).")


# TICKETS
elif page == "Tickets":
    st.header("IT Tickets")

    df = load_df("SELECT * FROM it_tickets;")

    # Status filter dropdown
    st.subheader("Filter by Status")
    ticket_status_options = ["All", "Resolved", "Open", "Waiting for User", "In Progress"]
    ticket_status = st.selectbox("Ticket Status", ticket_status_options)

    f = df.copy()
    if ticket_status != "All" and "status" in f.columns:
        f = f[f["status"] == ticket_status]

    st.dataframe(f, use_container_width=True)

    st.subheader("Ticket Status Breakdown (Pie)")
    if "status" in f.columns and not f.empty:
        status_count = f["status"].fillna("Unknown").value_counts().reset_index()
        status_count.columns = ["status", "count"]
        pie_chart(status_count, "status", "count", "Ticket Status Breakdown")
    else:
        st.info("No data for ticket status pie chart (after filtering).")

    st.subheader("Tickets Over Time (Line)")
    if "created_date" in f.columns and not f.empty:
        tmp = f.copy()
        tmp["created_date"] = safe_to_datetime(tmp["created_date"])
        tmp = tmp.dropna(subset=["created_date"])
        if tmp.empty:
            st.info("created_date exists, but none of the values are valid dates.")
        else:
            tmp["date"] = tmp["created_date"].dt.date
            daily = tmp.groupby("date").size().reset_index(name="count")
            daily["date"] = pd.to_datetime(daily["date"])
            line_chart(daily, "date", "count", "Tickets Created per Day")
    else:
        st.warning("No 'created_date' column found in it_tickets (or no data). Add it to enable time charts.")
