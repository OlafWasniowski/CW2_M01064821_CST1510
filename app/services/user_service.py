# app/services/user_service.py
from app.data.users import insert_user

def migrate_users_from_txt(path="DATA/users.txt"):
    """
    Reads a users.txt file where each line is:
    username,hashed_password
    and inserts them into the users table.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    username = parts[0].strip()
                    hashed = parts[1].strip()
                    insert_user(username, hashed)
        print("✓ Users migrated successfully")
    except FileNotFoundError:
        print(f"Users file not found at {path} — skipping user migration")
