# main.py
from app.data.schema import create_tables
from app.services.user_service import migrate_users_from_txt
from app.services.csv_loader import load_all_csv

from app.data.users import get_all_users
from app.data.incidents import get_all_incidents
from app.data.datasets import get_all_datasets
from app.data.tickets import get_all_tickets

def main():
    print("STEP 1: Creating tables...")
    create_tables()

    print("\nSTEP 2: Migrating users...")
    migrate_users_from_txt()

    print("\nSTEP 3: Loading CSV files...")
    load_all_csv()

    print("\nUsers in DB:")
    print(get_all_users())

    print("\nIncidents in DB:")
    print(get_all_incidents())

    print("\nDatasets in DB:")
    print(get_all_datasets())

    print("\nTickets in DB:")
    print(get_all_tickets())

if __name__ == "__main__":
    main()
