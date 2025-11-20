from app.data.schema import create_tables
from app.services.user_service import migrate_users_from_txt
from app.data.users import get_all_users
from app.data.incidents import get_all_incidents
from app.data.datasets import get_all_datasets


def main():
    print("STEP 1: Creating tables...")
    create_tables()

    print("STEP 2: Migrating users...")
    migrate_users_from_txt()

    print("\nUsers in DB:")
    print(get_all_users())

    print("\nIncidents in DB:")
    print(get_all_incidents())

    print("\nDatasets in DB:")
    print(get_all_datasets())




if __name__ == "__main__":
    main()
