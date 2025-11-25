# app/data/tickets.py
from app.data.db import connect_database

def insert_ticket(ticket_id, user, issue, status, created_date=None):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO it_tickets (ticket_id, user, issue, status, created_date)
        VALUES (?, ?, ?, ?, ?)
    """, (ticket_id, user, issue, status, created_date))

    conn.commit()
    conn.close()

def get_all_tickets():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT id, ticket_id, user, issue, status, created_date FROM it_tickets")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_ticket_status(ticket_id, new_status):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE it_tickets SET status = ? WHERE ticket_id = ?", (new_status, ticket_id))
    conn.commit()
    conn.close()

def delete_ticket(ticket_id):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
