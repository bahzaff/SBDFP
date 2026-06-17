import re
from config.database import run_query_mysql

def menu_crud_penghuni():
    """Menu 8: Kelola Data Penghuni"""
    while True:
        print("\n" + "="*40)
        print("       KELOLA DATA PENGHUNI       ")
        print("="*40)
        print("1. Tambah Penghuni (CREATE)")
        print("2. Lihat Daftar Penghuni (READ)")
        print("3. Ubah Data Penghuni (UPDATE)")
        print("4. Hapus Penghuni (DELETE)")
        print("0. Kembali ke Menu Utama")
        print("="*40)
        
        pilihan = input("Pilih aksi (0-4): ")
        
        if pilihan == '1':
            _create_penghuni()
        elif pilihan == '2':
            _read_penghuni()
        elif pilihan == '3':
            _update_penghuni()
        elif pilihan == '4':
            _delete_penghuni()
        elif pilihan == '0':
            break
        else:
            print("Pilihan tidak valid, silakan coba lagi.")

def _create_penghuni():
    print("\n--- TAMBAH PENGHUNI BARU (INSERT) ---")
    try:
        # Validasi ID Penghuni
        while True:
            id_input = input("ID Penghuni (Angka urut selanjutnya): ")
            if not id_input.isdigit():
                print("[Error] ID harus berupa angka bulat!")
                continue
            id_penghuni = int(id_input)
            
            # Cek apakah ID sudah ada di database
            cek = run_query_mysql("SELECT id_penghuni FROM Penghuni WHERE id_penghuni = %s", (id_penghuni,))
            if cek:
                print(f"[Error] ID {id_penghuni} sudah terpakai! Silakan masukkan ID yang belum ada.")
            else:
                break

        nama = input("Nama Lengkap: ")
        
        # Validasi Jenis Kelamin
        while True:
            jk = input("Jenis Kelamin (Laki-laki/Perempuan): ")
            if jk.lower() in ['laki-laki', 'perempuan']:
                jk = "Laki-laki" if jk.lower() == 'laki-laki' else "Perempuan"
                break
            print("[Error] Harap ketik persis 'Laki-laki' atau 'Perempuan'!")

        # Validasi No HP
        while True:
            no_hp = input("No HP (Minimal 10 angka): ")
            if no_hp.isdigit() and len(no_hp) >= 10:
                break
            print("[Error] No HP tidak valid! Harus berupa deretan angka minimal 10 digit tanpa spasi.")

        # Validasi Email
        while True:
            email = input("Email: ")
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                break
            print("[Error] Format email tidak valid! Harus memuat karakter '@' dan domain (contoh: a@gmail.com).")

        alamat = input("Alamat Asal: ")
        
        # RAW SQL QUERY INSERT
        query = """
            INSERT INTO Penghuni (id_penghuni, nama_penghuni, jenis_kelamin, no_hp, email, alamat_asal)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (id_penghuni, nama, jk, no_hp, email, alamat)
        
        # fetch=False karena perintah INSERT tidak mengembalikan baris tabel
        run_query_mysql(query, params, fetch=False)
        print(f"[Sukses] Permintaan penambahan data '{nama}' dikirim ke MySQL!")
    except Exception as e:
        print(f"[Error] Terjadi kesalahan: {e}")

def _read_penghuni():
    print("\n--- DAFTAR PENGHUNI (SELECT) ---")
    
    # RAW SQL QUERY SELECT
    query = "SELECT * FROM Penghuni ORDER BY id_penghuni ASC"
    data = run_query_mysql(query)
    
    if data:
        for row in data:
            print(f"[{row['id_penghuni']}] {row['nama_penghuni']:<15} | HP: {row['no_hp']:<13} | Alamat: {row['alamat_asal']}")
    else:
        print("Belum ada data penghuni di database.")

def _update_penghuni():
    print("\n--- UBAH DATA PENGHUNI (UPDATE) ---")
    _read_penghuni() # Tampilkan data agar user bisa melihat ID-nya
    
    try:
        print("\nMasukkan ID Penghuni yang ingin diubah...")
        id_input = input("ID: ")
        if not id_input.isdigit():
            print("[Error] Input ID harus berupa angka bulat!")
            return
        id_penghuni = int(id_input)
        
        # Cek apakah ID ada
        cek = run_query_mysql("SELECT id_penghuni FROM Penghuni WHERE id_penghuni = %s", (id_penghuni,))
        if not cek:
            print(f"[Error] Data dengan ID {id_penghuni} tidak ditemukan!")
            return
            
        nama_baru = input("Masukkan Nama Baru: ")
        
        # Validasi No HP
        while True:
            hp_baru = input("Masukkan No HP Baru (Minimal 10 angka): ")
            if hp_baru.isdigit() and len(hp_baru) >= 10:
                break
            print("[Error] No HP tidak valid! Harus berupa deretan angka minimal 10 digit tanpa spasi.")
        
        # RAW SQL QUERY UPDATE
        query = "UPDATE Penghuni SET nama_penghuni = %s, no_hp = %s WHERE id_penghuni = %s"
        params = (nama_baru, hp_baru, id_penghuni)
        
        run_query_mysql(query, params, fetch=False)
        print(f"[Sukses] Permintaan pembaruan data ID {id_penghuni} dikirim ke MySQL!")
    except Exception as e:
        print(f"[Error] Terjadi kesalahan: {e}")

def _delete_penghuni():
    print("\n--- HAPUS DATA PENGHUNI (DELETE) ---")
    _read_penghuni()
    
    try:
        print("\nMasukkan ID Penghuni yang ingin dihapus...")
        id_input = input("ID: ")
        if not id_input.isdigit():
            print("[Error] Input ID harus berupa angka bulat!")
            return
        id_penghuni = int(id_input)
        
        # Cek apakah ID ada di database terlebih dahulu
        cek = run_query_mysql("SELECT id_penghuni FROM Penghuni WHERE id_penghuni = %s", (id_penghuni,))
        if not cek:
            print(f"[Error] Penghuni dengan ID {id_penghuni} TIDAK DITEMUKAN di database!")
            return
            
        print("\n[PERINGATAN] Sesuai aturan Foreign Key, penghuni yang masih memiliki KONTRAK atau NOTIFIKASI aktif tidak bisa dihapus, kecuali kontraknya dihapus dulu.")
        konfirmasi = input(f"Yakin ingin menghapus data ID {id_penghuni}? (y/n): ")
        
        if konfirmasi.lower() == 'y':
            # RAW SQL QUERY DELETE
            query = "DELETE FROM Penghuni WHERE id_penghuni = %s"
            params = (id_penghuni,)
            
            run_query_mysql(query, params, fetch=False)
            print(f"[Sukses] Data ID {id_penghuni} berhasil dibasmi dari database MySQL!")
        else:
            print("Dibatalkan.")
    except Exception as e:
        print(f"[Error] Terjadi kesalahan saat menghapus (mungkin terhalang Foreign Key Kontrak): {e}")
