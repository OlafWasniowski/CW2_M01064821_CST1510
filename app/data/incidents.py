# app/data/incidents.py
from app.data.db import connect_database

def insert_incident(incident_id, timestamp, severity, category, status, description):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cyber_incidents (incident_id, timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (incident_id, timestamp, severity, category, status, description))

    conn.commit()
    conn.close()

def get_all_incidents():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT id, incident_id, timestamp, severity, category, status, description FROM cyber_incidents")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_incident_status(incident_id, new_status):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE cyber_incidents SET status = ? WHERE incident_id = ?", (new_status, incident_id))
    conn.commit()
    conn.close()

def delete_incident(incident_id):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    conn.commit()
    conn.close()
