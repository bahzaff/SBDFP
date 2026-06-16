from config.database import run_query_mysql

def menu_crud_penghuni():
    """Menu 8: Kelola Data Penghuni (Full CRUD dengan Raw SQL)"""
    while True:
        print("\n" + "="*40)
        print("       KELOLA DATA PENGHUNI (CRUD)      ")
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
        id_penghuni = int(input("ID Penghuni (Angka urut selanjutnya): "))
        nama = input("Nama Lengkap: ")
        jk = input("Jenis Kelamin (Laki-laki/Perempuan): ")
        no_hp = input("No HP: ")
        email = input("Email: ")
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
    except ValueError:
        print("[Error] ID Penghuni harus berupa angka bulat!")

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
        id_penghuni = int(input("ID: "))
        nama_baru = input("Masukkan Nama Baru: ")
        hp_baru = input("Masukkan No HP Baru: ")
        
        # RAW SQL QUERY UPDATE
        query = "UPDATE Penghuni SET nama_penghuni = %s, no_hp = %s WHERE id_penghuni = %s"
        params = (nama_baru, hp_baru, id_penghuni)
        
        run_query_mysql(query, params, fetch=False)
        print(f"[Sukses] Permintaan pembaruan data ID {id_penghuni} dikirim ke MySQL!")
    except ValueError:
        print("[Error] Input ID harus berupa angka bulat!")

def _delete_penghuni():
    print("\n--- HAPUS DATA PENGHUNI (DELETE) ---")
    _read_penghuni()
    
    try:
        print("\nMasukkan ID Penghuni yang ingin dihapus...")
        id_penghuni = int(input("ID: "))
        
        print("\n[PERINGATAN] Sesuai aturan Foreign Key, penghuni yang masih memiliki KONTRAK atau NOTIFIKASI aktif tidak bisa dihapus, kecuali kontraknya dihapus dulu.")
        konfirmasi = input(f"Yakin ingin menghapus data ID {id_penghuni}? (y/n): ")
        
        if konfirmasi.lower() == 'y':
            # RAW SQL QUERY DELETE
            query = "DELETE FROM Penghuni WHERE id_penghuni = %s"
            params = (id_penghuni,)
            
            run_query_mysql(query, params, fetch=False)
            print(f"[Sukses] Permintaan penghapusan data ID {id_penghuni} dikirim ke MySQL!")
        else:
            print("Dibatalkan.")
    except ValueError:
        print("[Error] Input ID harus berupa angka bulat!")
