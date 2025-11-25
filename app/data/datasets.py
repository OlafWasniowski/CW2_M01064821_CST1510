# app/data/datasets.py
from app.data.db import connect_database

def insert_dataset(dataset_id, name, rows, columns, uploaded_by, upload_date):
    conn = connect_database()
    cur = conn.cursor()

    # Use INSERT OR REPLACE so the CSV-provided dataset_id is preserved
    cur.execute("""
        INSERT OR REPLACE INTO datasets_metadata (dataset_id, name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_id, name, rows, columns, uploaded_by, upload_date))

    conn.commit()
    conn.close()

def get_all_datasets():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("SELECT dataset_id, name, rows, columns, uploaded_by, upload_date FROM datasets_metadata")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_dataset_rows(dataset_id, new_rows):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("UPDATE datasets_metadata SET rows = ? WHERE dataset_id = ?", (new_rows, dataset_id))
    conn.commit()
    conn.close()

def delete_dataset(dataset_id):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute("DELETE FROM datasets_metadata WHERE dataset_id = ?", (dataset_id,))
    conn.commit()
    conn.close()
