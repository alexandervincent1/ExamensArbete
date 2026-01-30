from backend.gmail import login, my_emails, get_latest_ids_from_gmail
from backend.db import initialize_database, save_message, get_latest_ids_from_db
from backend.ai import classify_email

running = False
thread = None

def check_and_watch():
    """Jämför Gmail med databasen för att "övervaka" """
    login()
    gmail_ids = get_latest_ids_from_gmail()
    conn = initialize_database()
    if not conn:
        print("databasen anslöt ej")
        return 0
    db_ids = get_latest_ids_from_db(conn)
    print(f"Gmail id = {gmail_ids} och Databas id = {db_ids}")


if __name__ == '__main__':
    check_and_watch()