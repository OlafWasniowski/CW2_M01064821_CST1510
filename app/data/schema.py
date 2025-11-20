from app.data.db import connect_database

def create_tables():
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT DEFAULT 'open',
        date TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        source TEXT,
        category TEXT,
        size INTEGER
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT DEFAULT 'open',
        created_date TEXT
    );
    """)

    conn.commit()
    conn.close()
