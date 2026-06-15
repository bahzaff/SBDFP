# Dokumentasi Sistem Manajemen Kos (KOSKU)

Dokumentasi ini berisi panduan penggunaan lengkap, teknologi pendukung, serta **Penjelasan Full Code (Bedah Kode)** secara utuh baris demi baris untuk seluruh file yang ada di dalam proyek ini.

---

## 🛠️ Teknologi dan Arsitektur
Proyek ini mengadaptasi arsitektur **MVC (Model-View-Controller)** sederhana yang dipecah menjadi beberapa modul Python.

**Stack Teknologi:**
- **Python 3.x**
- **MySQL** (Relasional)
- **MongoDB** (NoSQL)
- **Library Utama**: `mysql-connector-python`, `pymongo`, `pandas`, `plotext`, `python-dotenv`

---

## 🚀 Cara Penggunaan (Step-by-Step)
1. Buka terminal di folder proyek ini dan ketik: `pip install -r requirements.txt`
2. Gandakan `env.example` menjadi `.env` lalu isikan kredensial database Anda.
3. Pastikan MySQL dan MongoDB berjalan di laptop Anda.
4. Ketik `python main.py`
5. Tekan angka **`0`** lalu `Enter` untuk inisialisasi database awal.

---

## 📖 Penjelasan Full Code

Berikut adalah kode lengkap dari setiap file beserta penjelasan baris demi barisnya.

### 1. `main.py` (Menu Utama)
File ini adalah gerbang utama yang bertugas merutekan (router) navigasi aplikasi CLI.

```python
import sys
from controllers.setup_controller import setup_database
from controllers.mysql_controller import menu_cek_kamar_kosong, menu_cek_kontrak_hampir_habis, menu_rekap_tagihan_denda
from controllers.mongo_controller import menu_cari_review_mongodb
from controllers.chart_controller import menu_grafik_status_kamar, menu_grafik_distribusi_rating

# ==============================================================================
# PROGRAM UTAMA (CLI INTERAKTIF)
# ==============================================================================

def main():
    while True:
        print("\n" + "="*50)
        print("           SISTEM MANAJEMEN KOS (KOSKU)           ")
        print("="*50)
        print("0. Setup & Inisialisasi Database (Jalankan Awal)  ")
        print("-" * 50)
        print("1. Cek Kamar Kosong (MySQL)")
        print("2. Cek Kontrak Hampir Habis (MySQL)")
        print("3. Rekap Tagihan & Denda (MySQL JOIN)")
        print("4. Cari Review MongoDB (MongoDB)")
        print("5. Grafik Status Kamar (MySQL & Plotext)")
        print("6. Grafik Distribusi Rating (MongoDB & Plotext)")
        print("7. Keluar")
        print("="*50)
        
        pilihan = input("Pilih menu navigasi (0-7): ")
        
        if pilihan == '0':
            setup_database()
        elif pilihan == '1':
            menu_cek_kamar_kosong()
        elif pilihan == '2':
            menu_cek_kontrak_hampir_habis()
        elif pilihan == '3':
            menu_rekap_tagihan_denda()
        elif pilihan == '4':
            menu_cari_review_mongodb()
        elif pilihan == '5':
            menu_grafik_status_kamar()
        elif pilihan == '6':
            menu_grafik_distribusi_rating()
        elif pilihan == '7':
            print("Sistem ditutup. Terima kasih!")
            sys.exit(0)
        else:
            print("Pilihan menu tidak valid, silakan coba lagi.")

if __name__ == "__main__":
    main()
```
**Penjelasan Kode:**
- Baris 1-5: Mengimpor modul `sys` (untuk mematikan program) dan memanggil seluruh fungsi menu dari sub-folder `controllers/`.
- `def main():`: Ini adalah fungsi inisialisasi awal.
- `while True:`: Menjaga program agar tidak langsung tertutup setelah mengeksekusi 1 perintah. Program akan terus kembali mencetak menu sampai dipaksa mati.
- `pilihan = input(...)`: Menunggu ketikan keyboard dari user. Input tersebut dicek menggunakan `if-elif` untuk menjalankan fungsi yang sesuai.
- `sys.exit(0)`: Perintah mutlak untuk membunuh sistem operasi Python.
- `if __name__ == "__main__":`: Memastikan bahwa fungsi `main()` otomatis berjalan ketika file `main.py` dieksekusi secara langsung.

---

### 2. `config/database.py` (Koneksi Server)
File ini merangkum semua pengaturan dan keamanan penghubung antara Python dan Database.

```python
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
```
**Penjelasan Kode:**
- `load_dotenv()`: Fitur rahasia dari `.env`. Membaca kredensial agar *password database* tidak terekspos langsung di *source code*.
- `get_mysql_connection()`: Mencoba menyambung ke server MySQL menggunakan IP/localhost. Tanpa mendefinisikan "Nama Database" secara sengaja, agar saat *seeding* kita bisa mengeksekusi perintah *CREATE DATABASE* baru.
- `run_query_mysql()`: **Fungsi helper andalan.** Alih-alih menulis *cursor*, *try-except*, dan *commit* di setiap menu, kode tersebut ditampung terpusat di fungsi ini. Fungsi ini akan menerima string SQL, mengeksekusi `USE kosku_db`, menarik semua hasil (`fetchall`), lalu secara otomatis **menutup koneksi (`conn.close()`)** agar server tidak *overload*.
- `get_mongo_connection()`: Menghubungi MongoDB lewat IP port 27017. Baris `client.admin.command('ping')` krusial untuk "mengetuk gerbang" server agar kalau MongoDB mati, program langsung masuk ke area `except`.

---

### 3. `controllers/setup_controller.py` (Seeding / Impor Data Asli)
Membaca `dataset_koskufp.xlsx` & `review_seed.JSON`, membuat skema tabel, dan menginput datanya.

```python
import pandas as pd
import json
import os
from config.database import get_mysql_connection, get_mongo_connection

def setup_database():
    print("\n--- Memulai Setup & Inisialisasi Database ---")
    
    # 1. SETUP MYSQL
    mysql_conn = get_mysql_connection()
    if mysql_conn:
        try:
            cursor = mysql_conn.cursor()
            db_name = os.getenv("MYSQL_DATABASE", "kosku_db")
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # Drop secara terbalik (Child -> Parent)
            for tabel in ['Notifikasi', 'Denda', 'Pembayaran', 'Kontrak', 'Penghuni', 'Kamar']:
                cursor.execute(f"DROP TABLE IF EXISTS {tabel}")
            
            # Create Table (DDL)
            cursor.execute("""
                CREATE TABLE Kamar (
                    id_kamar INT PRIMARY KEY,
                    nomor_kamar VARCHAR(10),
                    tipe_kamar VARCHAR(50),
                    harga_sewa DECIMAL(15,2),
                    status_kamar VARCHAR(20),
                    fasilitas TEXT
                )
            """)
            # ... (Tabel Penghuni, Kontrak, Pembayaran, Denda, Notifikasi)
            
            print("[MySQL] Membaca dan mem-parsing dataset_koskufp.xlsx...")
            df = pd.read_excel('dataset_koskufp.xlsx', header=None)
            
            # Pandas iloc Coordinate Slicing
            kamar_df = df.iloc[4:12, 1:6].copy()
            kamar_df.columns = ['nomor_kamar', 'tipe_kamar', 'harga_sewa', 'status_kamar', 'fasilitas']
            kamar_df.insert(0, 'id_kamar', range(1, len(kamar_df) + 1))
            
            # ... (Slicing untuk tabel-tabel lainnya)
            
            def insert_df_to_mysql(data_df, table_name):
                data_df = data_df.where(pd.notnull(data_df), None) # Mengatasi nilai kosong (NaN -> NULL)
                cols = ", ".join([str(i) for i in data_df.columns.tolist()])
                placeholders = ", ".join(["%s"] * len(data_df.columns))
                sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
                
                data_tuples = [tuple(x) for x in data_df.to_numpy()]
                cursor.executemany(sql, data_tuples)
                mysql_conn.commit()

            insert_df_to_mysql(kamar_df, 'Kamar')
            # ... (Insert fungsi untuk lainnya)
            
            cursor.close()
        except Exception as e:
            print(f"[Error] Gagal saat setup MySQL: {e}")
        finally:
            if mysql_conn.is_connected():
                mysql_conn.close()
    
    # 2. SETUP MONGODB
    mongo_db = get_mongo_connection()
    if mongo_db is not None:
        try:
            collection = mongo_db['reviews']
            collection.drop() # Hapus duplikat
            
            with open('review_seed.JSON', 'r', encoding='utf-8') as file:
                content = file.read().strip()
                
            # Membersihkan Javascript Code
            if content.startswith('db.reviews.insertMany('):
                content = content.replace('db.reviews.insertMany(', '')
                if content.endswith(')'):
                    content = content[:-1]
                    
            reviews_data = json.loads(content)
            if reviews_data:
                collection.insert_many(reviews_data)
        except Exception as e:
            pass
```
**Penjelasan Kode:**
- `DROP TABLE IF EXISTS`: Mengapa dibalik dari urutan tabel aslinya? Karena MySQL memiliki aturan **Foreign Key**. Tabel anak (seperti Denda) yang bergantung pada tabel induk (Pembayaran) harus dilenyapkan lebih dulu, agar tidak terjadi constraint error saat di-drop.
- `df = pd.read_excel('...', header=None)`: Mengabaikan struktur Excel default karena di file Anda tabelnya berjejeran berantakan.
- `df.iloc[4:12, 1:6]`: Inilah cara mengekstrak tabel unik. `iloc` menseleksi secara spasial di baris ke-4 s/d 11, dan kolom ke-1 s/d 5.
- `df.where(pd.notnull(df), None)`: Pandas mengkonversi kotak excel yang kosong menjadi *NaN* (Not a Number). Fungsi ini mengganti NaN menjadi *None* agar dimengerti MySQL sebagai NULL murni.
- Blok *Replace String MongoDB*: Baris logika if untuk menghapus awalan `db.reviews.insertMany(` di dalam file JSON buatan Anda agar benar-benar menjadi file teks JSON murni sebelum diubah jadi dictionary Python (`json.loads`).

---

### 4. `controllers/mysql_controller.py` (Logika SQL Kompleks)
Sesuai arsitektur, semua sintaks SQL berada terpusat di modul ini.

```python
from config.database import run_query_mysql

def menu_cek_kamar_kosong():
    """Menu 1: Cek Kamar Kosong (MySQL)"""
    query = "SELECT nomor_kamar, tipe_kamar, harga_sewa, fasilitas FROM Kamar WHERE status_kamar = 'Tersedia'"
    data = run_query_mysql(query)
    # Output rendering...

def menu_cek_kontrak_hampir_habis():
    """Menu 2: Cek Kontrak Hampir Habis (MySQL)"""
    query = """
        SELECT p.nama_penghuni, k.nomor_kamar, ko.tanggal_selesai, DATEDIFF(ko.tanggal_selesai, CURDATE()) as sisa_hari
        FROM Kontrak ko
        JOIN Penghuni p ON ko.id_penghuni = p.id_penghuni
        JOIN Kamar k ON ko.id_kamar = k.id_kamar
        WHERE DATEDIFF(ko.tanggal_selesai, CURDATE()) BETWEEN -30 AND 90
          AND ko.status_kontrak = 'Aktif'
        ORDER BY ko.tanggal_selesai ASC
    """
    data = run_query_mysql(query)
    # Output rendering...

def menu_rekap_tagihan_denda():
    """Menu 3: Rekap Tagihan & Denda (MySQL Complex JOIN)"""
    query = """
        SELECT 
            p.nama_penghuni, 
            k.nomor_kamar, 
            pb.bulan_tagihan,
            pb.jumlah_bayar AS tagihan_pokok,
            IFNULL(d.jumlah_denda, 0) AS total_denda,
            (pb.jumlah_bayar + IFNULL(d.jumlah_denda, 0)) AS total_harus_dibayar,
            pb.status_bayar
        FROM Penghuni p
        JOIN Kontrak ko ON p.id_penghuni = ko.id_penghuni
        JOIN Kamar k ON ko.id_kamar = k.id_kamar
        JOIN Pembayaran pb ON ko.id_kontrak = pb.id_kontrak
        LEFT JOIN Denda d ON pb.id_pembayaran = d.id_pembayaran
    """
    data = run_query_mysql(query)
    # Output rendering...
```
**Penjelasan Kode:**
- `WHERE status_kamar = 'Tersedia'`: Filstrasi dasar satu tabel.
- `DATEDIFF(ko.tanggal_selesai, CURDATE())`: Fitur cerdas MySQL. Kurangi tanggal kontrak selesai dengan tanggal server hari ini (`CURDATE()`). Hasil outputnya berupa angka (jumlah hari).
- `BETWEEN -30 AND 90`: Nilai minus menandakan telat 30 hari. 90 menandakan tenggat 3 bulan.
- **Complex JOIN (Menu 3)**: Menggabungkan 5 tabel secara paralel (menggunakan *Primary ID* sebagai relasi).
- **`LEFT JOIN Denda`**: Denda adalah satu-satunya tabel yang wajib dihubungkan lewat "kiri" (LEFT). Kenapa? Karena data pembayaran normal (tanpa denda) tidak terdaftar di dalam tabel Denda. Jika Anda memakai *INNER JOIN*, pembayaran lunas tanpa denda tidak akan terbaca dan dilaporkan oleh sistem!
- **`IFNULL(jumlah_denda, 0)`**: Kalau denda kosong (NULL), MySQL ganti ke angka 0. Sangat vital untuk persamaan matematika Total Bayar, karena di bahasa SQL manapun: `1 Juta + NULL = NULL (Error)`.

---

### 5. `controllers/mongo_controller.py` (Pencarian NoSQL)
Memanfaatkan fitur canggih dari MongoDB (Regex, Query Terstruktur).

```python
import re
from config.database import get_mongo_connection

def menu_cari_review_mongodb():
    """Menu 4: Cari Review MongoDB"""
    kata_kunci = input("Masukkan keyword tag: ")
    rating_input = input("Masukkan minimal rating (1-5): ")
    
    mongo_db = get_mongo_connection()
    collection = mongo_db['reviews']
    query = {}
    
    if kata_kunci:
        regex_pattern = re.compile(f".*{kata_kunci}.*", re.IGNORECASE)
        query['tags'] = {"$in": [regex_pattern]}
        
    if rating_input.isdigit():
        query['rating'] = {"$gte": int(rating_input)}
        
    hasil_pencarian = collection.find(query)
    
    for review in hasil_pencarian:
        bintang = "★" * int(review.get('rating', 0))
        tags_str = ", ".join(review.get('tags', []))
        # Print ...
```
**Penjelasan Kode:**
- `query = {}`: Inisialisasi awal. Jika parameter input user dibiarkan kosong, MongoDB akan mencari seluruh tabel (karena `find({})` itu setara dengan `SELECT *`).
- `re.compile(..., re.IGNORECASE)`: Mengaktifkan mode *Regular Expression* pada Python yang anti huruf kapital. Pencarian kata "Kotor" tetap akan mengenai tag "kotor".
- `{"$in": [...]}`: Operator MongoDB In Array. Memerintahkan sistem untuk mencari adakah satu saja *array* tag yang mengandung pola di atas.
- `{"$gte": ...}`: Operator *Greater Than or Equal*. Mencari dokumen yang kolom rating-nya lebih besar dari atau setidaknya sama dengan batasan (*limit*) dari user.
- `bintang = "★" * ...`: Trik Python. Mengalikan simbol string sesuai dengan jumlah rating integer dari database (contoh: string bintang dikali 4, menghasilkan 4 jejer bintang).

---

### 6. `controllers/chart_controller.py` (Visualisasi Plotext CLI)
Modul untuk merender Bar Chart layaknya aplikasi GUI sungguhan di dalam terminal.

```python
import plotext as plt
from config.database import run_query_mysql, get_mongo_connection

def menu_grafik_status_kamar():
    """Menu 5: Grafik Status Kamar (Plotext & MySQL)"""
    query = "SELECT status_kamar, COUNT(*) as jumlah FROM Kamar GROUP BY status_kamar"
    data = run_query_mysql(query)
    
    labels = []
    values = []
    for row in data:
        labels.append(row['status_kamar'])
        values.append(row['jumlah'])
        
    plt.clear_data()
    plt.bar(labels, values, color="cyan", marker="sd")
    plt.title("Grafik Jumlah Kamar Berdasarkan Status (MySQL)")
    plt.theme("dark")
    plt.show()

def menu_grafik_distribusi_rating():
    """Menu 6: Grafik Distribusi Rating (Plotext & MongoDB)"""
    mongo_db = get_mongo_connection()
    collection = mongo_db['reviews']
    
    pipeline = [
        {"$group": {"_id": "$rating", "jumlah": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    hasil = list(collection.aggregate(pipeline))
    
    labels = []
    values = []
    for doc in hasil:
        labels.append(f"Bintang {doc['_id']}")
        values.append(doc['jumlah'])
        
    plt.clear_data()
    plt.bar(labels, values, color="green", marker="sd")
    plt.title("Grafik Distribusi Rating Penghuni (MongoDB)")
    plt.theme("dark")
    plt.show()
```
**Penjelasan Kode:**
- `GROUP BY status_kamar`: Aggregasi klasik di MySQL. Kolom yang tadinya puluhan diubah menjadi grup yang sama, lalu dihitungkan total kemunculannya lewat `COUNT(*)`.
- `pipeline = [...]` & `.aggregate(...)`: **Fitur Pipeline Aggregation di MongoDB**. Fitur ini jauh lebih kuat daripada Query SQL. Beroperasi seperti jalur pipa:
  - Pipa Pertama (`$group`): Satukan semua *review* yang memiliki rating yang sama, lalu buat variabel "jumlah" yang terus di-*increment* (`$sum: 1`).
  - Pipa Kedua (`$sort`): Lanjutkan data yang sudah dikelompokkan tersebut, lalu urutkan nilainya dari rating terkecil ke terbesar (`1` berarti *ascending*).
- `.append(...)`: Logika pemecahan *dictionary JSON/SQL* menjadi dua Array dasar secara terpisah (Array Sumbu X/Label, dan Array Sumbu Y/Value).
- `plt.clear_data()`: **Penting!** Mencegah grafik sebelumnya menumpuk jika fungsi ini dipanggil dua kali tanpa keluar program.
- `plt.bar(...)`: Merender kumpulan array di atas menjadi pilar/batang (*bar chart*) ke dalam layar terminal.
