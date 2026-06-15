import pandas as pd
import json
import os
from config.database import get_mysql_connection, get_mongo_connection

def setup_database():
    """Fungsi untuk membuat database, tabel, dan seeding dari dataset asli."""
    print("\n--- Memulai Setup & Inisialisasi Database ---")
    
    # ---------------------------------------------
    # 1. SETUP MYSQL (Dari file Excel)
    # ---------------------------------------------
    mysql_conn = get_mysql_connection()
    if mysql_conn:
        try:
            cursor = mysql_conn.cursor()
            db_name = os.getenv("MYSQL_DATABASE", "kosku_db")
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # Hapus tabel jika ada (reverse order foreign key)
            for tabel in ['Notifikasi', 'Denda', 'Pembayaran', 'Kontrak', 'Penghuni', 'Kamar']:
                cursor.execute(f"DROP TABLE IF EXISTS {tabel}")
            
            # Buat tabel baru
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
            cursor.execute("""
                CREATE TABLE Penghuni (
                    id_penghuni INT PRIMARY KEY,
                    nama_penghuni VARCHAR(100),
                    jenis_kelamin VARCHAR(20),
                    no_hp VARCHAR(20),
                    email VARCHAR(100),
                    alamat_asal TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE Kontrak (
                    id_kontrak INT PRIMARY KEY,
                    id_penghuni INT,
                    id_kamar INT,
                    tanggal_mulai DATE,
                    tanggal_selesai DATE,
                    status_kontrak VARCHAR(20),
                    FOREIGN KEY (id_penghuni) REFERENCES Penghuni(id_penghuni),
                    FOREIGN KEY (id_kamar) REFERENCES Kamar(id_kamar)
                )
            """)
            cursor.execute("""
                CREATE TABLE Pembayaran (
                    id_pembayaran INT PRIMARY KEY,
                    id_kontrak INT,
                    bulan_tagihan VARCHAR(50),
                    tanggal_jatuh_tempo DATE,
                    tanggal_bayar DATE,
                    jumlah_bayar DECIMAL(15,2),
                    status_bayar VARCHAR(20),
                    FOREIGN KEY (id_kontrak) REFERENCES Kontrak(id_kontrak)
                )
            """)
            cursor.execute("""
                CREATE TABLE Denda (
                    id_denda INT PRIMARY KEY,
                    id_pembayaran INT,
                    jumlah_denda DECIMAL(15,2),
                    alasan TEXT,
                    status_denda VARCHAR(20),
                    FOREIGN KEY (id_pembayaran) REFERENCES Pembayaran(id_pembayaran)
                )
            """)
            cursor.execute("""
                CREATE TABLE Notifikasi (
                    id_notifikasi INT PRIMARY KEY,
                    id_penghuni INT,
                    jenis_notifikasi VARCHAR(100),
                    tanggal_notifikasi DATE,
                    status_baca VARCHAR(20),
                    FOREIGN KEY (id_penghuni) REFERENCES Penghuni(id_penghuni)
                )
            """)
            
            # Ekstraksi manual dari data excel_koskufp.xlsx (posisi ter-hardcode)
            print("[MySQL] Membaca dan mem-parsing dataset_koskufp.xlsx...")
            df = pd.read_excel('dataset_koskufp.xlsx', header=None)
            
            kamar_df = df.iloc[4:12, 1:6].copy()
            kamar_df.columns = ['nomor_kamar', 'tipe_kamar', 'harga_sewa', 'status_kamar', 'fasilitas']
            kamar_df.insert(0, 'id_kamar', range(1, len(kamar_df) + 1))
            
            penghuni_df = df.iloc[15:25, 1:6].copy()
            penghuni_df.columns = ['nama_penghuni', 'jenis_kelamin', 'no_hp', 'email', 'alamat_asal']
            penghuni_df.insert(0, 'id_penghuni', range(1, len(penghuni_df) + 1))
            
            kontrak_df = df.iloc[28:38, 1:6].copy()
            kontrak_df.columns = ['id_penghuni', 'id_kamar', 'tanggal_mulai', 'tanggal_selesai', 'status_kontrak']
            kontrak_df.insert(0, 'id_kontrak', range(1, len(kontrak_df) + 1))
            
            pembayaran_df = df.iloc[12:32, 7:13].copy()
            pembayaran_df.columns = ['id_kontrak', 'bulan_tagihan', 'tanggal_jatuh_tempo', 'tanggal_bayar', 'jumlah_bayar', 'status_bayar']
            pembayaran_df.insert(0, 'id_pembayaran', range(1, len(pembayaran_df) + 1))
            
            denda_df = df.iloc[4:9, 7:11].copy()
            denda_df.columns = ['id_pembayaran', 'jumlah_denda', 'alasan', 'status_denda']
            denda_df.insert(0, 'id_denda', range(1, len(denda_df) + 1))
            
            notif_df = df.iloc[35:45, 7:11].copy()
            notif_df.columns = ['id_penghuni', 'jenis_notifikasi', 'tanggal_notifikasi', 'status_baca']
            notif_df.insert(0, 'id_notifikasi', range(1, len(notif_df) + 1))
            
            def insert_df_to_mysql(data_df, table_name):
                data_df = data_df.where(pd.notnull(data_df), None) # Ubah NaN ke None/NULL
                cols = ", ".join([str(i) for i in data_df.columns.tolist()])
                placeholders = ", ".join(["%s"] * len(data_df.columns))
                sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
                
                data_tuples = [tuple(x) for x in data_df.to_numpy()]
                cursor.executemany(sql, data_tuples)
                mysql_conn.commit()
                print(f"  -> {len(data_tuples)} baris sukses di-insert ke tabel '{table_name}'")

            insert_df_to_mysql(kamar_df, 'Kamar')
            insert_df_to_mysql(penghuni_df, 'Penghuni')
            insert_df_to_mysql(kontrak_df, 'Kontrak')
            insert_df_to_mysql(pembayaran_df, 'Pembayaran')
            insert_df_to_mysql(denda_df, 'Denda')
            insert_df_to_mysql(notif_df, 'Notifikasi')
            
            cursor.close()
            print("[MySQL] Setup selesai dan berhasil.\n")
        except FileNotFoundError:
            print("[Error] File dataset_koskufp.xlsx tidak ditemukan di folder root!")
        except Exception as e:
            print(f"[Error] Gagal saat setup MySQL: {e}")
        finally:
            if mysql_conn.is_connected():
                mysql_conn.close()
    
    # ---------------------------------------------
    # 2. SETUP MONGODB (Dari file JSON)
    # ---------------------------------------------
    mongo_db = get_mongo_connection()
    if mongo_db is not None:
        try:
            print("[MongoDB] Membaca file review_seed.JSON...")
            collection = mongo_db['reviews']
            collection.drop()
            
            with open('review_seed.JSON', 'r', encoding='utf-8') as file:
                content = file.read().strip()
                
            # Pembersih jika isinya query insertMany MongoDB Shell
            if content.startswith('db.reviews.insertMany('):
                content = content.replace('db.reviews.insertMany(', '')
                if content.endswith(')'):
                    content = content[:-1]
                    
            reviews_data = json.loads(content)
                
            if reviews_data:
                collection.insert_many(reviews_data)
                print(f"  -> {len(reviews_data)} dokumen sukses di-insert ke collection 'reviews'")
            
            print("[MongoDB] Setup selesai dan berhasil.\n")
        except FileNotFoundError:
            print("[Error] File review_seed.JSON tidak ditemukan di folder root!")
        except Exception as e:
            print(f"[Error] Gagal saat setup MongoDB: {e}")
