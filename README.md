# Dokumentasi Sistem Manajemen Kos (KOSKU)

Dokumentasi ini berisi panduan penggunaan lengkap, teknologi pendukung, serta **Penjelasan Full Code (Bedah Kode)** yang dibedah **per fungsi / per bagian** secara mendetail.

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
1. **Instalasi**: Buka terminal di folder proyek ini dan ketik: `pip install -r requirements.txt`
2. **Nyalakan Server**: Buka aplikasi **XAMPP Control Panel**, lalu nyalakan (*Start*) modul **MySQL**. Pastikan juga server **MongoDB** berjalan di laptop Anda.
3. **Jalankan Aplikasi**: Ketik `python main.py`
4. **Seeding (Wajib Pertama Kali)**: Di Menu Utama, tekan angka **`0`** lalu `Enter` untuk membuat dan menyuntikkan data dari `dataset_koskufp.xlsx` & `review_seed.JSON` ke database komputer Anda.

---

## 📖 Penjelasan Full Code (Per Fungsi / Bagian)

Berikut adalah bedah tuntas seluruh *source code* yang dipecah dan dijelaskan setiap blok fungsinya.

### 1. File: `main.py` (Menu Utama)

#### Bagian 1: Import Modul
```python
import sys
from controllers.setup_controller import setup_database
from controllers.mysql_controller import menu_cek_kamar_kosong, menu_cek_kontrak_hampir_habis, menu_rekap_tagihan_denda
from controllers.mongo_controller import menu_cari_review_mongodb
from controllers.chart_controller import menu_grafik_status_kamar, menu_grafik_distribusi_rating
```
**Penjelasan:** 
- `import sys`: Digunakan khusus untuk mengeksekusi perintah mematikan program secara total (`sys.exit`).
- `from controllers...`: Memanggil seluruh fungsi operasional yang sudah disebar ke sub-folder `controllers/` agar file utama ini tetap bersih.

#### Bagian 2: Fungsi Main (Antarmuka CLI)
```python
def main():
    while True:
        print("\n" + "="*50)
        print("           SISTEM MANAJEMEN KOS (KOSKU)           ")
        print("="*50)
        print("0. Setup & Inisialisasi Database (Jalankan Awal)  ")
        # ... (Print Pilihan 1 sampai 7)
        
        pilihan = input("Pilih menu navigasi (0-7): ")
```
**Penjelasan:** 
- `while True:`: Konstruksi perulangan abadi. Ini memastikan bahwa setelah pengguna menjalankan suatu fitur (misal: Cek Kamar Kosong), program tidak langsung tertutup, melainkan akan kembali mencetak Menu Utama berulang kali sampai user sengaja memilih menu nomor 7 (Keluar).
- `input(...)`: Meminta masukan teks dari pengguna dan menyimpannya di variabel `pilihan`.

#### Bagian 3: Router Menu & Exit
```python
        if pilihan == '0':
            setup_database()
        elif pilihan == '1':
            menu_cek_kamar_kosong()
        # ... (elif 2 sampai 6)
        elif pilihan == '7':
            print("Sistem ditutup. Terima kasih!")
            sys.exit(0)
        else:
            print("Pilihan menu tidak valid, silakan coba lagi.")

if __name__ == "__main__":
    main()
```
**Penjelasan:**
- Rangkaian `if-elif` digunakan layaknya *Switch-Case* untuk mengarahkan pilihan user ke fungsi controller yang tepat.
- `sys.exit(0)`: Perintah ini memberi sinyal ke *Sistem Operasi Windows* untuk menghentikan terminal Python tanpa *error* (kode 0 berarti aman).
- `if __name__ == "__main__":`: Baris sakti di Python. Memastikan fungsi `main()` hanya berjalan apabila file `main.py` yang diklik/dijalankan langsung, bukan ketika di-import oleh file lain.

---

### 2. File: `config/database.py` (Koneksi Server)

#### Bagian 1: Inisialisasi Environment
```python
import os
import mysql.connector
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
```
**Penjelasan:** 
- `load_dotenv()`: Bertugas membaca file `.env` di proyek Anda lalu memasukkan kredensial rahasia (seperti Password database) ke dalam memori aplikasi secara aman.

#### Bagian 2: Konektor MySQL
```python
def get_mysql_connection():
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
```
**Penjelasan:**
- Mencoba menghubungi MySQL menggunakan IP/Localhost yang disetting. 
- **Penting:** Kami *sengaja* tidak menambahkan parameter `database=...` di awal koneksi ini karena pada saat awal di-run, database `kosku_db` itu sendiri belum ada dan baru akan dibuat melalui *Menu 0*.

#### Bagian 3: Fungsi Pembantu (Helper) MySQL
```python
def run_query_mysql(query, params=None, fetch=True):
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
        # handle error...
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
```
**Penjelasan:**
- Ini adalah fungsi tulang punggung aplikasi (Helper). Tujuannya agar kita tidak menulis ulang blok koneksi panjang ini di setiap fitur. Semua Controller MySQL hanya perlu memanggil fungsi ini.
- `cursor(dictionary=True)`: Memaksa MySQL agar mengembalikan data dalam format JSON/Dictionary (Contoh: `row['nama']`), bukan dalam format tuple indeks kaku (`row[0]`).
- `USE kosku_db`: Otomatis berpindah ke database `kosku_db` sebelum mengeksekusi SQL.
- `finally: conn.close()`: Menjamin agar gerbang server MySQL langsung ditutup setelah query selesai dieksekusi agar memori tidak bocor/overload.

#### Bagian 4: Konektor MongoDB
```python
def get_mongo_connection():
    try:
        client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"), serverSelectionTimeoutMS=2000)
        client.admin.command('ping') 
        db = client[os.getenv("MONGO_DB", "kosku_db")]
        return db
    # ...
```
**Penjelasan:**
- Membuat koneksi *client* ke port MongoDB (`27017`).
- `serverSelectionTimeoutMS=2000`: Membatasi waktu tunggu menjadi maksimal 2 detik.
- `client.admin.command('ping')`: Secara harafiah mengetuk pintu server. Tanpa baris ini, aplikasi python mungkin tidak sadar kalau MongoDB lokal Anda sedang mati.

---

### 3. File: `controllers/setup_controller.py` (Seeding / Import)

#### Bagian 1: Inisiasi Database & Tabel Baru (Drop)
```python
# ... import pandas, json, dll
def setup_database():
    mysql_conn = get_mysql_connection()
    cursor = mysql_conn.cursor()
    db_name = os.getenv("MYSQL_DATABASE", "kosku_db")
    
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    cursor.execute(f"USE {db_name}")
    
    for tabel in ['Notifikasi', 'Denda', 'Pembayaran', 'Kontrak', 'Penghuni', 'Kamar']:
        cursor.execute(f"DROP TABLE IF EXISTS {tabel}")
```
**Penjelasan:**
- `CREATE DATABASE`: Murni DDL (Data Definition Language) untuk membangun skema.
- `DROP TABLE` Terbalik: Urutan nama array dimulai dari 'Notifikasi' mundur hingga ke 'Kamar'. Mengapa? Karena aturan ketat **Foreign Key Constraint** MySQL; Tabel "Anak" yang menumpang pada tabel "Induk" harus dihapus terlebih dahulu, jika tidak MySQL akan menolaknya.

#### Bagian 2: Pembuatan DDL (Tabel MySQL)
```python
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
    # (Kode di atas diulang untuk tabel Penghuni, Kontrak, dll)
```
**Penjelasan:**
- Membentuk kerangka masing-masing tabel. Harga sewa didefinisikan sebagai `DECIMAL` untuk menyimpan nominal uang yang sangat akurat tanpa pembulatan *float*.

#### Bagian 3: Membaca & Memotong Koordinat Excel
```python
    df = pd.read_excel('dataset_koskufp.xlsx', header=None)
    
    kamar_df = df.iloc[4:12, 1:6].copy()
    kamar_df.columns = ['nomor_kamar', 'tipe_kamar', 'harga_sewa', 'status_kamar', 'fasilitas']
    kamar_df.insert(0, 'id_kamar', range(1, len(kamar_df) + 1))
    # (Kode serupa dilakukan untuk Penghuni, Kontrak, dst)
```
**Penjelasan:**
- Dikarenakan file *dataset_koskufp.xlsx* Anda menyatukan banyak tabel di sembarang tempat pada sheet yang sama, maka `pandas` diinstruksikan tidak membaca *Header* (`header=None`).
- `.iloc[4:12, 1:6]`: Inilah rahasianya. Fitur ini menyeleksi sebuah "kotak" (seperti proses *drag* kursor) secara eksak yang dimulai dari Baris indeks ke-4 sampai 11, dan Kolom indeks ke-1 sampai 5. Data di luar koordinat tersebut diabaikan.
- `.insert(0, 'id_kamar'...)`: Menyisipkan kolom `Primary Key` secara massal (mulai angka 1, 2, 3...) langsung di awal tabel sebelum didorong ke database.

#### Bagian 4: Eksekusi Insert Multi-Data
```python
    def insert_df_to_mysql(data_df, table_name):
        data_df = data_df.where(pd.notnull(data_df), None) 
        cols = ", ".join([str(i) for i in data_df.columns.tolist()])
        placeholders = ", ".join(["%s"] * len(data_df.columns))
        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        
        data_tuples = [tuple(x) for x in data_df.to_numpy()]
        cursor.executemany(sql, data_tuples)
        mysql_conn.commit()
```
**Penjelasan:**
- `.where(pd.notnull)`: Jika excel punya kotak yang kosong, Pandas mengubahnya jadi *NaN* (Not a Number). Modifikasi ini mengubah *NaN* menjadi nilai asli `None` (NULL di SQL).
- `executemany`: Alih-alih melakukan *query insert* satu per satu yang sangat lambat, fitur ini menembakkan keseluruhan ribuan baris Excel (Array Tuples) sekaligus dalam 1 milidetik. 

#### Bagian 5: Mengupas Data JSON MongoDB
```python
    mongo_db = get_mongo_connection()
    collection = mongo_db['reviews']
    collection.drop()
    
    with open('review_seed.JSON', 'r', encoding='utf-8') as file:
        content = file.read().strip()
        
    if content.startswith('db.reviews.insertMany('):
        content = content.replace('db.reviews.insertMany(', '')
        if content.endswith(')'):
            content = content[:-1]
            
    reviews_data = json.loads(content)
    collection.insert_many(reviews_data)
```
**Penjelasan:**
- Karena file `review_seed.JSON` Anda aslinya berisi sebuah sintaks fungsi *MongoDB Shell*, ia ditolak oleh parser JSON Python.
- Oleh karena itu, skrip Python ini mengidentifikasi jika ada awalan `db.reviews.insertMany(`. Kalau iya, maka teks kata awalan itu dan tanda kurung penutupnya di bagian akhir akan dihancurkan (`.replace`). Hasilnya, tersisa murni data *JSON Array* yang dapat dicerna utuh ke MongoDB dengan `insert_many`.

---

### 4. File: `controllers/mysql_controller.py` (SQL Logic)

#### Bagian 1: Cek Kamar Kosong (Menu 1)
```python
from config.database import run_query_mysql

def menu_cek_kamar_kosong():
    query = "SELECT nomor_kamar, tipe_kamar, harga_sewa, fasilitas FROM Kamar WHERE status_kamar = 'Tersedia'"
    data = run_query_mysql(query)
    
    for row in data:
        print(f"Kamar: {row['nomor_kamar']} | Tipe: {row['tipe_kamar']}")
```
**Penjelasan:** 
- Operasi SELECT paling dasar. Memfilter dari 1 tabel dengan parameter kaku `WHERE status_kamar = 'Tersedia'`.

#### Bagian 2: Cek Kontrak Hampir Habis (Menu 2)
```python
def menu_cek_kontrak_hampir_habis():
    query = """
        SELECT p.nama_penghuni, k.nomor_kamar, ko.tanggal_selesai, DATEDIFF(ko.tanggal_selesai, CURDATE()) as sisa_hari
        FROM Kontrak ko
        JOIN Penghuni p ON ko.id_penghuni = p.id_penghuni
        JOIN Kamar k ON ko.id_kamar = k.id_kamar
        WHERE DATEDIFF(ko.tanggal_selesai, CURDATE()) BETWEEN -30 AND 90
          AND ko.status_kontrak = 'Aktif'
    """
    data = run_query_mysql(query)
    # Output rendering...
```
**Penjelasan:** 
- `JOIN`: Menyambungkan 3 tabel (Kontrak, Penghuni, Kamar) karena data yang dicari terpecah.
- `DATEDIFF(ko.tanggal_selesai, CURDATE())`: Rumus canggih SQL! Secara dinamis menghitung selisih jarak hari dari *tanggal selesai kontrak* terhadap *tanggal sistem hari ini*. 
- `BETWEEN -30 AND 90`: Memfilter hanya kontrak yang telat 30 hari hingga yang akan habis 3 bulan ke depan.

#### Bagian 3: Rekap Tagihan & Denda (Menu 3 - Complex JOIN)
```python
def menu_rekap_tagihan_denda():
    query = """
        SELECT 
            p.nama_penghuni, k.nomor_kamar, pb.jumlah_bayar,
            IFNULL(d.jumlah_denda, 0) AS total_denda,
            (pb.jumlah_bayar + IFNULL(d.jumlah_denda, 0)) AS total_harus_dibayar
        FROM Penghuni p
        JOIN Kontrak ko ON p.id_penghuni = ko.id_penghuni
        JOIN Kamar k ON ko.id_kamar = k.id_kamar
        JOIN Pembayaran pb ON ko.id_kontrak = pb.id_kontrak
        LEFT JOIN Denda d ON pb.id_pembayaran = d.id_pembayaran
    """
    data = run_query_mysql(query)
    # Output rendering...
```
**Penjelasan:** 
- **Complex JOIN**: Proses penggabungan besar-besaran 5 buah tabel paralel.
- **`LEFT JOIN Denda`**: Tabel Denda harus disambung lewat *KIRI* (LEFT). Alasannya, tidak semua data pembayaran masuk ke tabel denda (karena ada orang bayar tepat waktu). Jika menggunakan *INNER JOIN*, orang yang teladan/lunas tanpa denda *tidak akan muncul sama sekali* di hasil laporannya!
- **`IFNULL(jumlah_denda, 0)`**: Kalau hasil *LEFT JOIN* tidak menemukan denda, nilainya akan berisi *NULL*. Jika angka *Jumlah Bayar* ditambah *NULL*, hasilnya akan *ERROR* secara matematika SQL. Oleh karena itu, `IFNULL` menyulap nilai NULL tersebut menjadi angka 0 agar persamaan matematikanya aman.

---

### 5. File: `controllers/crud_controller.py` (Menu 7 - Kelola Data Penghuni)
Menu interaktif tambahan untuk membuktikan operasi manipulasi data secara utuh menggunakan *Raw SQL* murni.

#### Bagian 1: Insert (Tambah Penghuni)
```python
def _create_penghuni():
    # input(...) variabel
    query = """
        INSERT INTO Penghuni (id_penghuni, nama_penghuni, jenis_kelamin, no_hp, email, alamat_asal)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (id_penghuni, nama, jk, no_hp, email, alamat)
    run_query_mysql(query, params, fetch=False)
```
**Penjelasan:** Menggunakan injeksi string tuple `(%s)` yang terhindar dari lubang keamanan *SQL Injection*. Parameter `fetch=False` penting karena perintah `INSERT` tidak mengembalikan bentuk *tabel* dari MySQL.

#### Bagian 2: Update (Ubah Data) & Delete (Hapus)
```python
def _update_penghuni():
    # ...
    query = "UPDATE Penghuni SET nama_penghuni = %s, no_hp = %s WHERE id_penghuni = %s"
    run_query_mysql(query, (nama_baru, hp_baru, id_penghuni), fetch=False)

def _delete_penghuni():
    # ...
    query = "DELETE FROM Penghuni WHERE id_penghuni = %s"
    run_query_mysql(query, (id_penghuni,), fetch=False)
```
**Penjelasan:** 
- `UPDATE ... SET`: Mengubah data kolom spesifik berdasarkan ID.
- `DELETE FROM`: Menghapus satu baris penuh dari tabel Penghuni. **Catatan:** Sesuai aturan *Relational Database*, eksekusi `DELETE` ini akan otomatis ditolak/error oleh sistem jika penghuni tersebut masih memiliki record di tabel "Kontrak", sehingga data pembayaran yang sedang berjalan tidak akan pernah rusak.

---

### 6. File: `controllers/mongo_controller.py` (Pencarian NoSQL)

#### Pencarian Canggih MongoDB (Menu 4)
```python
import re
from config.database import get_mongo_connection

def menu_cari_review_mongodb():
    kata_kunci = input("Masukkan keyword tag: ")
    rating_input = input("Masukkan minimal rating: ")
    
    mongo_db = get_mongo_connection()
    collection = mongo_db['reviews']
    query = {}
    
    if kata_kunci:
        regex_pattern = re.compile(f".*{kata_kunci}.*", re.IGNORECASE)
        query['tags'] = {"$in": [regex_pattern]}
        
    if rating_input.isdigit():
        query['rating'] = {"$gte": int(rating_input)}
        
    hasil_pencarian = collection.find(query)
```
**Penjelasan:**
- Logika NoSQL lebih dinamis (Object/Dictionary) dibandingkan String kaku di MySQL. Dictionary `query = {}` bisa membesar secara elastis.
- `re.compile(..., re.IGNORECASE)`: Mengubah kata kunci menjadi format Regex, agar pencarian anti sensitif terhadap huruf kapital (KOTOR = kotor).
- `{"$in": [...]}`: Perintah "In-Array" spesifik MongoDB. Memerintahkan server memeriksa apakah *keyword* user bersarang di dalam serpihan *List of Tags*.
- `{"$gte": ...}`: *Greater Than or Equal*. Mencari otomatis semua rating yang setidaknya sama persis atau lebih besar (contoh: minta rating minimal 3, maka rating 4 dan 5 otomatis tampil).

---

### 6. File: `controllers/chart_controller.py` (Visualisasi Data)

#### Bagian 1: Chart SQL Dasar (Menu 5)
```python
import plotext as plt
from config.database import run_query_mysql, get_mongo_connection

def menu_grafik_status_kamar():
    query = "SELECT status_kamar, COUNT(*) as jumlah FROM Kamar GROUP BY status_kamar"
    data = run_query_mysql(query)
    
    labels = []
    values = []
    for row in data:
        labels.append(row['status_kamar'])
        values.append(row['jumlah'])
        
    plt.clear_data()
    plt.bar(labels, values, color="cyan", marker="sd")
    plt.show()
```
**Penjelasan:**
- `GROUP BY`: Memilah total baris berdasarkan isian kolom 'Tersedia' vs 'Terisi'. `COUNT(*)` menotal masing-masing.
- Terjadi *Data Formatting*. Output Dictionary SQL itu pecah menjadi 2 array: `labels` (untuk Sumbu X) dan `values` (Sumbu Y).
- `plt.clear_data()`: Mengosongkan memori kanvas visualisasi, agar ketika menu ditekan berkali-kali, gambarnya tidak bertumpuk/menduplikat diri. `plt.bar` mengeksekusi konversi ke gambar batang (Bar Chart) di terminal CLI.

#### Bagian 2: Chart Agregasi MongoDB (Menu 6)
```python
def menu_grafik_distribusi_rating():
    mongo_db = get_mongo_connection()
    collection = mongo_db['reviews']
    
    pipeline = [
        {"$group": {"_id": "$rating", "jumlah": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    hasil = list(collection.aggregate(pipeline))
    
    # ... render ke plotext sama seperti di atas
```
**Penjelasan:**
- Berbeda dengan `find()`, MongoDB memiliki teknologi super mutakhir bernama **Aggregation Pipeline**.
- Bekerja bagai ban berjalan di pabrik:
  - **Tahap Pipa 1 (`$group`)**: Mengumpulkan dokumen yang memiliki Primary ID (`_id`) / Nilai `$rating` yang persis sama. Kemudian, ia akan menekan tuas konter (`$sum: 1`) setiap kali ada dokumen yang masuk ke grup tersebut.
  - **Tahap Pipa 2 (`$sort`)**: Setelah nilai dijumlahkan, data diputar dan diurutkan menaik (*Ascending* angka 1). Artinya, Bintang 1 akan ditaruh di awal antrian, dan Bintang 5 di akhir antrian. Selanjutnya hasil disuapkan langsung ke library plotext.
