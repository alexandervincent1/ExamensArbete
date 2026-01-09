import warnings
import sys
import os

warnings.filterwarnings("ignore")
os.environ["GRPC_PYTHON_LOG_LEVEL"] = "error"

stderr_backup = sys.stderr
sys.stderr = open(os.devnull, 'w')

from backend.db import initialize_database, save_message
from backend.gmail import my_emails, login, logout
from backend.ai import classify_email



sys.stderr = stderr_backup


def main():
    try:
        antal = int(input("Hur många mail vill du spara? "))
    except ValueError:
        antal = 10

    conn = initialize_database()
    if conn:
        msgs = my_emails(antal)

        for m in msgs:
            print(f"\n🔄 Klassificerar: {m['subject']}")
            
            ai_result = classify_email(m['subject'], m['body'])
            
            save_message(
                conn,
                m['id'],
                m['sender'],
                m['subject'],
                m['body'],
                ai_result.get('folder'),
                ai_result.get('summary'),
                ai_result.get('subject')
            )
            
            print(f"✅ Sparat: {m['subject']}")
            print(f"   📁 Mapp: {ai_result.get('folder')}")
            print(f"   📝 Sammanfattning: {ai_result.get('summary')}")
            print(f"   🏷️  Nytt ämne: {ai_result.get('subject')}")

        conn.close()
        print(f"\n🎉 Klart! {len(msgs)} mejl sparade med AI-klassificering.")
    else:
        print("❌ Kunde inte ansluta till databasen.")

if __name__ == "__main__":
    login()
    main()
    logout()