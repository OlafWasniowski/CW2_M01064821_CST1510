from app.data.users import insert_user

def migrate_users_from_txt(path="DATA/users.txt"):
    with open(path, "r") as file:
        for line in file:
            username, hashed_password = line.strip().split(",")
            insert_user(username, hashed_password)

    print("✓ Users migrated successfully")
