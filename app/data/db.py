# app/data/db.py
import sqlite3
from pathlib import Path

# Put the DB inside the app/data folder so it's always the one used by the app
DB_PATH = Path(__file__).resolve().parent / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Return a sqlite3 connection to the project's database file."""
    return sqlite3.connect(str(db_path))
