from app.data.db import connect_database

def insert_dataset(name, source, category, size):
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO datasets_metadata (name, source, category, size)
        VALUES (?, ?, ?, ?)
    """, (name, source, category, size))

    conn.commit()
    conn.close()


def get_all_datasets():
    conn = connect_database()
    cur = conn.cursor()

    cur.execute("SELECT * FROM datasets_metadata")
    rows = cur.fetchall()

    conn.close()
    return rows
