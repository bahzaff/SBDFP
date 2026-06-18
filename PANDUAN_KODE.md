# PANDUAN KODE (BEDAH APLIKASI KOSKU)

Dokumen ini adalah panduan lengkap untuk memahami isi dari setiap file `.py` yang ada di dalam *project* ini. Sangat berguna untuk bahan presentasi atau menjawab pertanyaan dosen mengenai alur program.

---

## 1. File `main.py`
File ini adalah "Pintu Gerbang Utama" dari aplikasi. Isinya murni hanya untuk mengatur menu (UI) dan tidak memproses data sama sekali.

### A. Fungsi `main()`
Fungsi ini memisahkan pengguna menjadi dua *Role* (Pemilik vs Penghuni).
```python
def main():
    while True:
        print("\n" + "="*50)
        print("       SELAMAT DATANG DI SISTEM MANAJEMEN KOS     ")
        print("="*50)
        print("1. Masuk sebagai Pemilik Kos")
        print("2. Masuk sebagai Penghuni/Publik")
        print("0. Keluar Aplikasi")
        
        pilihan = input("Pilih role Anda (0-2): ")
        if pilihan == '1':
            menu_pemilik()
        elif pilihan == '2':
            menu_penghuni()
        elif pilihan == '0':
            sys.exit(0)
```
**Tugas Utama:** Menangani input Role dan mengarahkan pengguna ke sub-menu yang tepat.

### B. Fungsi `menu_pemilik()` & `menu_penghuni()`
Ini adalah kumpulan *If-Else* panjang yang memanggil fungsi-fungsi dari folder `controllers`.
```python
def menu_penghuni():
    # ... Print daftar menu ...
    pilihan = input("Pilih menu navigasi (0-3): ")
    if pilihan == '1':
        menu_cari_review_mongodb()
    elif pilihan == '2':
        menu_beri_review()
    elif pilihan == '3':
        menu_lihat_notifikasi()
```
**Tugas Utama:** Mengalihkan pilihan pengguna ke spesialis (*controller*) yang benar.

---

## 2. File `config/database.py`
Ini adalah "Jantung" aplikasi. Berisi kode untuk menghubungkan Python ke server MySQL (XAMPP) dan MongoDB.

### A. Fungsi `get_mysql_connection()` & `get_mongo_connection()`
```python
def get_mysql_connection():
    # ...
    conn = mysql.connector.connect(host="localhost", user="root", password="")
    return conn

def get_mongo_connection():
    # ...
    client = MongoClient("mongodb://localhost:27017/")
    return client["kosku_db"]
```
**Tugas Utama:** Membuat jembatan komunikasi ke server database berdasarkan setting bawaan.

### B. Fungsi `run_query_mysql()`
```python
def run_query_mysql(query, params=None, fetch=True):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"USE kosku_db")
    cursor.execute(query, params)
    result = cursor.fetchall() if fetch else None
    conn.commit()
    return result
```
**Tugas Utama:** Mengambil string SQL murni (misal `"SELECT *"`), mengeksekusinya ke MySQL, lalu mengembalikan datanya dalam format *Dictionary* agar mudah di-*looping*.

---

## 3. File `controllers/setup_controller.py`
### Fungsi `setup_database()`
```python
def setup_database():
    # ... Drop tables, Create Tables ...
    kamar_df = pd.read_csv('data/kamar.csv')
    for index, row in kamar_df.iterrows():
        # Insert ke MySQL
```
**Tugas Utama:** Saat dipanggil lewat Menu 0, fungsi ini merubuhkan database lama (DROP), membuat tabel baru (CREATE TABLE), membaca ke-6 file CSV menggunakan Pandas, lalu menyuntikkan (INSERT) data tersebut ke dalam MySQL. Termasuk juga menyuntikkan data ke MongoDB.

---

## 4. File `controllers/mysql_controller.py`
Berisi fungsi-fungsi canggih berbasis `SELECT` & `JOIN` MySQL, serta fitur Notifikasi.

### A. Fungsi `menu_cek_kontrak_hampir_habis()` & `menu_rekap_tagihan_denda()`
```python
def menu_rekap_tagihan_denda():
    query = """
        SELECT p.nama_penghuni, k.nomor_kamar, pb.jumlah_bayar AS tagihan_pokok,
               IFNULL(d.jumlah_denda, 0) AS total_denda
        FROM Penghuni p
        JOIN Kontrak ko ON p.id_penghuni = ko.id_penghuni
        JOIN Kamar k ON ko.id_kamar = k.id_kamar
        JOIN Pembayaran pb ON ko.id_kontrak = pb.id_kontrak
        LEFT JOIN Denda d ON pb.id_pembayaran = d.id_pembayaran
    """
    data = run_query_mysql(query)
```
**Tugas Utama:** Menjalankan Query JOIN kompleks untuk menampilkan informasi penting di Terminal.

### B. Fungsi `menu_kirim_notifikasi()` & `menu_lihat_notifikasi()`
```python
# Kirim Notif
query_insert = "INSERT INTO Notifikasi (id_notifikasi, id_penghuni, jenis_notifikasi, tanggal_notifikasi, status_baca) VALUES (%s, %s, %s, %s, %s)"

# Lihat Notif
query_select = "SELECT * FROM Notifikasi WHERE id_penghuni = %s"
query_update = "UPDATE Notifikasi SET status_baca = 'Sudah Dibaca' WHERE id_penghuni = %s"
```
**Tugas Utama:** Melakukan komunikasi dua arah antara pemilik (INSERT) dan penghuni (SELECT lalu UPDATE).

---

## 5. File `controllers/crud_controller.py`
Berisi seluruh operasi Input/Update/Delete khusus untuk tabel Penghuni.

### Fungsi `_delete_penghuni()` (Fitur Soft-Delete / Checkout)
```python
def _delete_penghuni(id_penghuni):
    # 1. Update Kontrak jadi Selesai
    run_query_mysql("UPDATE Kontrak SET status_kontrak = 'Selesai' WHERE id_penghuni = %s AND status_kontrak = 'Aktif'", (id_penghuni,), fetch=False)
    
    # 2. Update status Kamar jadi Tersedia
    run_query_mysql("UPDATE Kamar SET status_kamar = 'Tersedia' WHERE id_kamar = %s", (id_kamar,), fetch=False)
```
**Tugas Utama:** Saat penghuni dihapus, program tidak melakukan `DELETE FROM Penghuni`, melainkan meng-`UPDATE` tabel Kontrak dan Kamar untuk menjaga riwayat keuangan tetap utuh.

---

## 6. File `controllers/mongo_controller.py`
Berisi fitur Ulasan (Review) yang datanya disimpan di MongoDB.

### A. Fungsi `menu_beri_review()`
```python
def menu_beri_review():
    # 1. Cek hak akses ke MySQL
    cek = run_query_mysql("SELECT * FROM Kontrak WHERE id_penghuni = %s AND id_kamar = %s", ...)
    
    # 2. Simpan ke MongoDB (Dengan fitur menimpa ulasan lama / Upsert)
    filter_query = {"id_penghuni": id_penghuni, "id_kamar": id_kamar}
    update_data = {"$set": {"komentar": komentar, "rating": rating}}
    collection.update_one(filter_query, update_data, upsert=True)
```
**Tugas Utama:** Melakukan verifikasi *Cross-Database* (ngecek kontrak ke MySQL), baru setelah diizinkan, datanya disuntikkan ke MongoDB menggunakan metode `upsert` (Update or Insert).

### B. Fungsi `menu_cari_review_mongodb()`
```python
def menu_cari_review_mongodb():
    query = {'id_kamar': int(id_kamar_input)}
    hasil = collection.find(query)
    # Loop dan print hasil...
```
**Tugas Utama:** Menjalankan perintah `find()` dari library PyMongo berdasarkan ID kamar yang dicari.

---

## 7. File `controllers/chart_controller.py`
Berisi visualisasi data statistik di Terminal menggunakan Plotext.

```python
def menu_grafik_status_kamar():
    query = "SELECT status_kamar, COUNT(*) as jumlah FROM Kamar GROUP BY status_kamar"
    data = run_query_mysql(query)
    
    # ... Memasukkan data ke labels dan values ...
    plt.bar(labels, values)
    plt.show()
```
**Tugas Utama:** Mengambil hasil penghitungan (`COUNT(*) GROUP BY`) dari database, lalu menyuapkannya ke dalam *library* `plotext` agar digambarkan menjadi grafik batang (*Bar Chart*).
