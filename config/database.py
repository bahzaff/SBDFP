import os
import mysql.connector
from pymongo import MongoClient
from dotenv import load_dotenv

# Memuat konfigurasi dari .env
load_dotenv()

def get_mysql_connection():
    """Membuat koneksi ke server MySQL (kosku_db)."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"[Error] Gagal menghubungkan ke MySQL: {err}")
        return None

def run_query_mysql(query, params=None, fetch=True):
    """Fungsi helper untuk mengeksekusi query MySQL."""
    conn = get_mysql_connection()
    if not conn: return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"USE {os.getenv('MYSQL_DATABASE', 'kosku_db')}")
        cursor.execute(query, params)
        result = cursor.fetchall() if fetch else None
        conn.commit()
        return result
    except Exception as e:
        print(f"[Error] Eksekusi query gagal: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_mongo_connection():
    """Membuat koneksi ke server MongoDB."""
    try:
        client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"), serverSelectionTimeoutMS=2000)
        client.admin.command('ping') 
        db = client[os.getenv("MONGO_DB", "kosku_db")]
        return db
    except Exception as e:
        print(f"[Error] Gagal menghubungkan ke MongoDB: {e}")
        return None
