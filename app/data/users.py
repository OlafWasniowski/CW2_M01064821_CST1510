# app/data/users.py
from app.data.db import connect_database

def insert_user(username, password_hash, role="user"):
    conn = connect_database()
    cur = conn.cursor()

    # use INSERT OR IGNORE so we don't crash on duplicate usernames
    cur.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
    """, (username, password_hash, role))

    conn.commit()
    conn.close()

def get_all_users():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_user_by_username(username):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def update_user_role(username, new_role):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
    conn.commit()
    conn.close()

def delete_user(username):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
