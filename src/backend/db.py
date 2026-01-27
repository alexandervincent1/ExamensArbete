import mysql.connector
import json
import os
from dotenv import load_dotenv

BASE_PATH = "/Users/master/Desktop/ExamensArbete/src/"
load_dotenv(BASE_PATH + '.env')


def initialize_database():
    try:
        with open(BASE_PATH + 'config/db_config.json') as f:
            config = json.load(f)
        config['password'] = os.getenv('DB_PASSWORD')
        db_name = config.pop('database')
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gmail_messages (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                message_id VARCHAR(255) NOT NULL UNIQUE,
                sender VARCHAR(255),
                subject TEXT,
                body LONGTEXT,
                ai_folder VARCHAR(100),
                ai_summary LONGTEXT,
                ai_subject TEXT,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (ai_folder)
            )
        """)
        conn.commit()
        print(f"✅ Ansluten till DB ('{db_name}')")
        return conn
    except Exception as e:
        print(f"DB-fel: {e}")
        return None


def save_message(conn, message_id, sender, subject, body, ai_folder=None, ai_summary=None, ai_subject=None):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO gmail_messages (message_id, sender, subject, body, ai_folder, ai_summary, ai_subject)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE ai_folder=VALUES(ai_folder), ai_summary=VALUES(ai_summary), ai_subject=VALUES(ai_subject)
    """, (message_id, sender, subject, body, ai_folder, ai_summary, ai_subject))
    conn.commit()


def email_exists(conn, message_id):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM gmail_messages WHERE message_id = %s", (message_id,))
    result = cursor.fetchone() is not None
    cursor.close()
    return result


def get_existing_message_ids(conn):
    """Hämta alla sparade message_id:n för snabb lookup"""
    cursor = conn.cursor()
    cursor.execute("SELECT message_id FROM gmail_messages")
    ids = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return ids


def get_latest_message_id_from_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT message_id
        FROM gmail_messages
        ORDER BY imported_at DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    cursor.close()
    return row[0] if row else None

