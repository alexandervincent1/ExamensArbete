import mysql.connector 
import json          
import os            
from dotenv import load_dotenv 

BASE_PATH = "/Users/master/Desktop/ExamensArbete/"
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
    CREATE TABLE IF NOT EXISTS 
    email_analysis 
    (
        id INT AUTO_INCREMENT PRIMARY KEY,
        message_id VARCHAR(255) UNIQUE NOT NULL,
        sender VARCHAR(255),
        subject TEXT,
        classification VARCHAR(50),
        reason TEXT,
        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(TABLE_SQL)
    print("Tabell 'email_analysis' är klar.")


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
    

if __name__ == '__main__':
    print("--- Verifierar Databasmodul ---")
    conn = initialize_database()
    
    if conn:
        print("✅ DB-modulen är redo för användning.")
        conn.close()
    else:
        print("Fel 5")