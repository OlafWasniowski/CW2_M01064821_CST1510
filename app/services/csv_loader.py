# app/services/csv_loader.py
import csv
from app.data.incidents import insert_incident
from app.data.datasets import insert_dataset
from app.data.tickets import insert_ticket

def load_cyber_incidents(path="DATA/cyber_incidents.csv"):
    try:
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # CSV header: incident_id,timestamp,severity,category,status,description
                incident_id = int(row.get("incident_id") or 0)
                timestamp = row.get("timestamp", "")
                severity = row.get("severity", "")
                category = row.get("category", "")
                status = row.get("status", "")
                description = row.get("description", "")
                insert_incident(incident_id, timestamp, severity, category, status, description)
        print("✓ cyber_incidents loaded")
    except FileNotFoundError:
        print(f"cyber_incidents CSV not found at {path}, skipping.")

def load_datasets_metadata(path="DATA/datasets_metadata.csv"):
    try:
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # CSV header: dataset_id,name,rows,columns,uploaded_by,upload_date
                dataset_id = int(row.get("dataset_id") or 0)
                name = row.get("name", "")
                rows_count = int(row.get("rows") or 0)
                columns_count = int(row.get("columns") or 0)
                uploaded_by = row.get("uploaded_by", "")
                upload_date = row.get("upload_date", "")
                insert_dataset(dataset_id, name, rows_count, columns_count, uploaded_by, upload_date)
        print("✓ datasets_metadata loaded")
    except FileNotFoundError:
        print(f"datasets_metadata CSV not found at {path}, skipping.")

def load_it_tickets(path="DATA/it_tickets.csv"):
    try:
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # attempt to handle many ticket formats; common fields: id,user,issue,status,created_date
                ticket_id = int(row.get("ticket_id") or row.get("id") or 0)
                user = row.get("user") or row.get("username") or ""
                issue = row.get("issue") or row.get("description") or ""
                status = row.get("status") or ""
                created_date = row.get("created_date") or row.get("created") or ""
                insert_ticket(ticket_id, user, issue, status, created_date)
        print("✓ it_tickets loaded")
    except FileNotFoundError:
        print(f"it_tickets CSV not found at {path}, skipping.")

def load_all_csv():
    load_cyber_incidents()
    load_datasets_metadata()
    load_it_tickets()
