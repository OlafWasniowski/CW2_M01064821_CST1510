import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# -----------------------------------------
# Streamlit page settings (title + layout)
# -----------------------------------------
# "wide" gives you more horizontal space which is nicer for tables and charts.
st.set_page_config(page_title="Cyber Intelligence Dashboard", layout="wide")


# -----------------------------------------
# HARD-CODED LOGIN DETAILS (simple demo auth)
# -----------------------------------------
# NOTE: This is NOT secure for real world use (credentials are inside the code),
# but it’s perfectly fine for a coursework/demo so you can protect the dashboard page.
# The login also works with credentials from the hashed users and passwords.
VALID_USERNAME = "Olaf"
VALID_PASSWORD = "admin123"

# -----------------------------------------
# Session State (keeps user logged in)
# -----------------------------------------
# Streamlit re-runs the script from top-to-bottom whenever you interact with widgets.
# st.session_state lets us "remember" things like whether the user has logged in.
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# -----------------------------------------
# Login Page UI
# -----------------------------------------
def login_page():
    # Simple login screen
    st.title("Login to Cyber Intelligence Dashboard")
    st.write("Enter your credentials to continue.")

    # User input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # When button is clicked it validates the credentials of the user
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            # If correct -> set logged_in flag to True and refresh the app
            st.session_state.logged_in = True
            st.rerun()
        else:
            # If incorrect -> show error message
            st.error("Invalid username or password.")


# If the user is NOT logged in, show the login page and stop the script here.
# st.stop() prevents the dashboard from loading underneath.
if not st.session_state.logged_in:
    login_page()
    st.stop()

# -----------------------------------------
# DB HELPERS
# -----------------------------------------
# This is the path to your SQLite database file.
# IMPORTANT: it’s a relative path which means it can run streamlit from the project root folder.
DB_PATH = "app/data/intelligence_platform.db"


def get_conn():
    """
    Opens a connection to the SQLite database.
    We wrap this in a function so it’s easy to reuse.
    """
    return sqlite3.connect(DB_PATH)


def load_df(query: str) -> pd.DataFrame:
    """
    Runs a SQL query and returns the results as a Pandas DataFrame.
    We also make sure the DB connection always closes (finally block).
    """
    conn = get_conn()
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


# -----------------------------------------
# Chart helper functions (Altair)
# -----------------------------------------
# NOTE: We use Altair here because it usually works out of the box with Streamlit.
# I previously hit errors using matplotlib/plotly because they weren’t installed / configured.
# Altair is lightweight and integrates well with st.altair_chart().
def pie_chart(count_df: pd.DataFrame, label_col: str, value_col: str, title: str):
    """
    Builds a pie chart from a "count_df" DataFrame that looks like:
    label_col | value_col
    ---------------------
    A         | 10
    B         | 5
    """
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
    """
    Builds a line chart from a DataFrame with a datetime column and a numeric column.
    Example:
    date       | count
    ------------------
    2024-01-01 | 2
    2024-01-02 | 5
    """
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
    """
    Converts a column to datetime safely.
    errors="coerce" means invalid dates become NaT (so they can be dropped).
    """
    return pd.to_datetime(series, errors="coerce")


# -----------------------------------------
# DASHBOARD (main UI after login)
# -----------------------------------------
st.title("Cyber Intelligence Dashboard")
st.caption("Streamlit dashboard pulling data from SQLite")

# Sidebar navigation: lets the user switch between different datasets/pages.
page = st.sidebar.selectbox("Navigation", ["Users", "Cyber Incidents", "Datasets", "Tickets"])


# =========================================================
# PAGE 1: USERS
# =========================================================
if page == "Users":
    st.header("Users Table")

    # Loads in full users table into a DataFrame
    df = load_df("SELECT * FROM users;")
    st.dataframe(df, use_container_width=True)

    # Pie chart: how many users are in each role
    st.subheader("Users by Role (Pie)")
    if "role" in df.columns and not df.empty:
        role_count = df["role"].fillna("Unknown").value_counts().reset_index()
        role_count.columns = ["role", "count"]
        pie_chart(role_count, "role", "count", "Users by Role")
    else:
        st.info("No 'role' column found (or table is empty), so no pie chart.")

    # Line chart: users over time
    # NOTE: users table doesn’t have a real created_date, so this creates a fake / proxy timeline to make the line chart possible.
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


# =========================================================
# PAGE 2: CYBER INCIDENTS
# =========================================================
elif page == "Cyber Incidents":
    st.header("Cyber Incidents")

    # Loads the incidents table
    df = load_df("SELECT * FROM cyber_incidents;")

    # Filters (dropdowns) so user can narrow down results
    st.subheader("Filters")
    colA, colB, colC = st.columns(3)

    sev_options = ["All", "Low", "Medium", "High", "Critical"]
    cat_options = ["All", "Phishing", "DDoS", "Malware", "Misconfiguration", "Unauthorized Access"]
    status_options = ["All", "Resolved", "Open", "Waiting for User", "In Progress", "Closed"]

    severity = colA.selectbox("Severity", sev_options)
    category = colB.selectbox("Category", cat_options)
    status = colC.selectbox("Status", status_options)

    # Apply filters to a copy of the dataframe (so we don’t modify original df)
    f = df.copy()
    if severity != "All" and "severity" in f.columns:
        f = f[f["severity"] == severity]
    if category != "All" and "category" in f.columns:
        f = f[f["category"] == category]
    if status != "All" and "status" in f.columns:
        f = f[f["status"] == status]

    # Show filtered table
    st.dataframe(f, use_container_width=True)

    # Pie chart: severity distribution after filtering
    st.subheader("Severity Distribution (Pie)")
    if "severity" in f.columns and not f.empty:
        sev_count = f["severity"].fillna("Unknown").value_counts().reset_index()
        sev_count.columns = ["severity", "count"]
        pie_chart(sev_count, "severity", "count", "Incident Severity Breakdown")
    else:
        st.info("No data for severity pie chart (after filtering).")

    # Line chart: incidents over time (grouped per day)
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


# =========================================================
# PAGE 3: DATASETS METADATA
# =========================================================
elif page == "Datasets":
    st.header("Datasets Metadata")

    # Loads the datasets table
    df = load_df("SELECT * FROM datasets_metadata;")
    st.dataframe(df, use_container_width=True)

    # Pie chart: datasets uploaded by which user
    st.subheader("Uploads by User (Pie)")
    if "uploaded_by" in df.columns and not df.empty:
        uploader_count = df["uploaded_by"].fillna("Unknown").value_counts().reset_index()
        uploader_count.columns = ["uploaded_by", "count"]
        pie_chart(uploader_count, "uploaded_by", "count", "Datasets Uploaded by User")
    else:
        st.info("No 'uploaded_by' column found (or table is empty).")

    # Line chart: uploads over time (grouped per day)
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


# =========================================================
# PAGE 4: IT TICKETS
# =========================================================
elif page == "Tickets":
    st.header("IT Tickets")

    # Loads the tickets table
    df = load_df("SELECT * FROM it_tickets;")

    # Status filter dropdown (matches your coursework requirement)
    st.subheader("Filter by Status")
    ticket_status_options = ["All", "Resolved", "Open", "Waiting for User", "In Progress"]
    ticket_status = st.selectbox("Ticket Status", ticket_status_options)

    # Apply ticket status filter
    f = df.copy()
    if ticket_status != "All" and "status" in f.columns:
        f = f[f["status"] == ticket_status]

    # Show filtered tickets table
    st.dataframe(f, use_container_width=True)

    # Pie chart: ticket status breakdown
    st.subheader("Ticket Status Breakdown (Pie)")
    if "status" in f.columns and not f.empty:
        status_count = f["status"].fillna("Unknown").value_counts().reset_index()
        status_count.columns = ["status", "count"]
        pie_chart(status_count, "status", "count", "Ticket Status Breakdown")
    else:
        st.info("No data for ticket status pie chart (after filtering).")

    # Line chart: tickets created over time
    # NOTE: This requires a real created_date column in your it_tickets table.
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