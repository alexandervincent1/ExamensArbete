from backend.db import initialize_database, save_message
from backend.gmail import myEmails

def main():

    try:
        antal = int(input("Hur många mail vill du spara? "))
    except ValueError:
        antal = 10  

    conn = initialize_database()
    if conn:

        msgs = myEmails(antal)

        for m in msgs:
            save_message(conn, m['id'], m['sender'], m['subject'], m['body'])
            print(f"✅ Sparat mail: {m['subject']} från {m['sender']}")

        conn.close()
    else:
        print("❌ Kunde inte ansluta till databasen.")

if __name__ == "__main__":
    main()