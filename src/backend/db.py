import mysql.connector 
import json          
import os            
from dotenv import load_dotenv 

BASE_PATH = "/Users/master/Desktop/ExamensArbete/src/"
load_dotenv(BASE_PATH + '.env') 

def load_db_config():
    config_path = BASE_PATH + 'config/db_config.json'

    try:
        with open(config_path,'r') as f:
            config = json.load(f)
            config['password'] = os.getenv('DB_PASSWORD') 
            return config
    except FileNotFoundError:
        print("Fel 1")
        return None
    except Exception:
        print("Fel 2")
        return None


def create_analysis_table(cursor):
    TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS gmail_messages (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        message_id VARCHAR(255) NOT NULL UNIQUE,
        sender VARCHAR(255) DEFAULT NULL,
        subject TEXT DEFAULT NULL,
        body LONGTEXT DEFAULT NULL,
        ai_summary LONGTEXT DEFAULT NULL,
        ai_subject TEXT DEFAULT NULL,
        ai_folder VARCHAR(100) DEFAULT NULL,
        received_at TIMESTAMP NULL DEFAULT NULL,
        imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_ai_folder (ai_folder),
        FULLTEXT INDEX ft_subject_body (subject, body, ai_summary)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    try:
        cursor.execute(TABLE_SQL)
        conn = getattr(cursor, 'connection', None) or getattr(cursor, '_connection', None) or getattr(cursor, 'cnx', None)
        if conn:
            conn.commit()
        else:
            try:
                cursor.execute("COMMIT")
            except Exception:
                print("Varning: kunde inte committa — anropande kod måste göra commit.")
        print("Tabell 'gmail_messages' skapad/uppdaterad.")
    except Exception as e:
        print("Fel vid skapande av tabell:", e)


def initialize_database():
    config = load_db_config()
    if not config:
        return None

    DB_NAME = config.pop('database') 
    
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password']
        )
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}") 

        print(f"✅ Ansluten till DB ('{DB_NAME}')")
        create_analysis_table(cursor)

        return conn

    except mysql.connector.Error as err:
        print("Fel 4")
        print(f"Detaljer: {err}")
        return None


def save_message(conn, message_id, sender, subject, body, ai_folder=None, ai_summary=None, ai_subject=None):
    cursor = conn.cursor()
    sql = """
    INSERT INTO gmail_messages (message_id, sender, subject, body, ai_folder, ai_summary, ai_subject, received_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    ON DUPLICATE KEY UPDATE 
        sender=VALUES(sender), 
        subject=VALUES(subject), 
        body=VALUES(body),
        ai_folder=VALUES(ai_folder),
        ai_summary=VALUES(ai_summary),
        ai_subject=VALUES(ai_subject)
    """
    cursor.execute(sql, (message_id, sender, subject, body, ai_folder, ai_summary, ai_subject))
    conn.commit()
    cursor.close()

if __name__ == '__main__':
    print("--- Verifierar Databasmodul ---")
    conn = initialize_database()
    
    if conn:
        print("✅ DB-modulen är redo för användning.")
        conn.close()
    else:
        print("Fel 5")