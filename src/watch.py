import time
from backend.gmail import login, my_emails, get_latest_ids_from_gmail
from backend.db import initialize_database, save_message, get_latest_ids_from_db
from backend.ai import classify_email


def check_and_watch():
    login()
    
    conn = initialize_database()
    if not conn:
        return
    
    gmail_ids = get_latest_ids_from_gmail()
    db_ids = get_latest_ids_from_db(conn)
    
    print(f"📧 Gmail: {gmail_ids}")
    print(f"💾 DB:    {db_ids}")
    
    new_ids = set(gmail_ids) - set(db_ids)
    
    if not new_ids:
        print("✅ Inga nya mejl")
        conn.close()
        return
    
    emails = my_emails(50)
    
    for m in emails:
        if m['id'] in new_ids:
            ai = classify_email(m['subject'], m['body'])
            save_message(conn, m['id'], m['sender'], m['subject'], m['body'], ai.get('folder'), ai.get('summary'), ai.get('subject'), m['timestamp'])
            print(f"  ✅ {ai.get('folder')}: {m['subject'][:40]}")
    
    conn.close()


if __name__ == '__main__':
    print("👁️ Bevakning (var 30:e sek) - Ctrl+C för att avsluta\n")
    while True:
        check_and_watch()
        time.sleep(20)

