from app.data.db import connect_database

def insert_incident(title, severity, status="open", date=None):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cyber_incidents (title, severity, status, date)
        VALUES (?, ?, ?, ?)
    """, (title, severity, status, date))

    conn.commit()
    conn.close()


def get_all_incidents():
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("SELECT * FROM cyber_incidents")
    rows = cur.fetchall()

    conn.close()
    return rows
