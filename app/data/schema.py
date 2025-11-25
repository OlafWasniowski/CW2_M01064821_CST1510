# app/data/schema.py
from app.data.db import connect_database

def create_tables():
    conn = connect_database()
    cur = conn.cursor()

    # USERS TABLE (username + hashed password + role)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        );
    """)

    # CYBER INCIDENTS (match your cyber_incidents.csv)
    # csv columns: incident_id,timestamp,severity,category,status,description
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER,
            timestamp TEXT,
            severity TEXT,
            category TEXT,
            status TEXT,
            description TEXT
        );
    """)

    # DATASETS METADATA (match your datasets_metadata.csv)
    # csv columns: dataset_id,name,rows,columns,uploaded_by,upload_date
    cur.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id INTEGER PRIMARY KEY,
            name TEXT,
            rows INTEGER,
            columns INTEGER,
            uploaded_by TEXT,
            upload_date TEXT
        );
    """)

    # IT TICKETS (simple ticket table)
    # assume it_tickets.csv has columns: id,user,issue,status,created_date (if present)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER,
            user TEXT,
            issue TEXT,
            status TEXT,
            created_date TEXT
        );
    """)

    conn.commit()
    conn.close()
