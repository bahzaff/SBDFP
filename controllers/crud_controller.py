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
        print(f"\n[Sukses] Data Penghuni '{nama}' berhasil ditambahkan ke database!")
        
        # FITUR TAMBAHAN: Pilih Kamar & Buat Kontrak (Multi-table Transaction)
        print("\n--- PILIH KAMAR (OPSIONAL) ---")
        kamar_kosong = run_query_mysql("SELECT id_kamar, nomor_kamar, harga_sewa FROM Kamar WHERE status_kamar = 'Tersedia'")
        
        if kamar_kosong:
            print("Daftar kamar yang tersedia saat ini:")
            for k in kamar_kosong:
                print(f"- ID: {k['id_kamar']} | Nomor: {k['nomor_kamar']} | Harga: Rp{k['harga_sewa']:,.0f}")
                
            while True:
                pilih_kamar = input("\nMasukkan ID Kamar untuk disewa (Ketik 0 jika lewati): ")
                if not pilih_kamar.isdigit():
                    print("[Error] Masukkan angka valid!")
                    continue
                
                id_kamar_pilihan = int(pilih_kamar)
                if id_kamar_pilihan == 0:
                    print("Oke, penghuni ditambahkan tanpa kamar (hanya daftar tunggu).")
                    break
                    
                # Cek apakah kamar valid dan kosong
                kamar_valid = next((k for k in kamar_kosong if k['id_kamar'] == id_kamar_pilihan), None)
                if kamar_valid:
                    from datetime import datetime, timedelta
                    
                    # 1. Generate id_kontrak baru
                    max_kontrak = run_query_mysql("SELECT MAX(id_kontrak) as max_id FROM Kontrak")
                    new_id_kontrak = (max_kontrak[0]['max_id'] or 0) + 1 if max_kontrak else 1
                    
                    # 2. Minta Input Durasi Sewa
                    while True:
                        durasi_input = input("Durasi sewa (dalam bulan): ")
                        if durasi_input.isdigit() and int(durasi_input) > 0:
                            durasi_bulan = int(durasi_input)
                            break
                        print("[Error] Masukkan angka bulan yang valid (contoh: 1, 6, 12)!")
                    
                    # 3. Set Tanggal (1 bulan diasumsikan 30 hari)
                    tgl_mulai = datetime.now()
                    tgl_selesai = tgl_mulai + timedelta(days=30 * durasi_bulan)
                    
                    # 4. Insert Tabel Kontrak
                    q_kontrak = """
                        INSERT INTO Kontrak (id_kontrak, id_penghuni, id_kamar, tanggal_mulai, tanggal_selesai, status_kontrak)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    p_kontrak = (new_id_kontrak, id_penghuni, id_kamar_pilihan, tgl_mulai.strftime('%Y-%m-%d'), tgl_selesai.strftime('%Y-%m-%d'), 'Aktif')
                    run_query_mysql(q_kontrak, p_kontrak, fetch=False)
                    
                    # 5. Update Tabel Kamar
                    q_update_kamar = "UPDATE Kamar SET status_kamar = 'Terisi' WHERE id_kamar = %s"
                    run_query_mysql(q_update_kamar, (id_kamar_pilihan,), fetch=False)
                    
                    print(f"[Sukses Luar Biasa] Penghuni '{nama}' resmi menempati Kamar '{kamar_valid['nomor_kamar']}' selama {durasi_bulan} Bulan ke depan!")
                    break
                else:
                    print("[Error] ID Kamar tidak ditemukan atau sedang tidak tersedia! Pilih ID yang ada di daftar.")
        else:
            print("Sayang sekali, semua kamar saat ini PENUH. Penghuni didaftarkan tanpa kamar.")
            
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
            
        # Cek apakah dia punya kontrak aktif
        q_kontrak = "SELECT id_kontrak, id_kamar FROM Kontrak WHERE id_penghuni = %s AND status_kontrak = 'Aktif'"
        kontrak_aktif = run_query_mysql(q_kontrak, (id_penghuni,))
        
        if not kontrak_aktif:
            print(f"[Info] Penghuni ID {id_penghuni} saat ini tidak memiliki kamar / kontrak aktif yang bisa dihapus.")
            return
            
        print(f"\n[PERINGATAN] Penghapusan (Delete) ini akan mengakhiri kontrak penghuni dan mengubah status kamar menjadi 'Tersedia'.")
        print("Data riwayat pembayaran dan penghuni TETAP AMAN (Tidak Dihapus dari Database).")
        konfirmasi = input(f"Yakin memproses Hapus Penghuni ID {id_penghuni}? (y/n): ")
        
        if konfirmasi.lower() == 'y':
            # 1. Update Kontrak jadi Selesai
            run_query_mysql("UPDATE Kontrak SET status_kontrak = 'Selesai' WHERE id_penghuni = %s AND status_kontrak = 'Aktif'", (id_penghuni,), fetch=False)
            
            # 2. Update status semua kamar yang disewa penghuni tersebut jadi Tersedia
            for k in kontrak_aktif:
                run_query_mysql("UPDATE Kamar SET status_kamar = 'Tersedia' WHERE id_kamar = %s", (k['id_kamar'],), fetch=False)
                
            print(f"[Sukses] Proses Hapus ID {id_penghuni} berhasil! Kamar telah dibebaskan.")
        else:
            print("Dibatalkan.")
    except Exception as e:
        print(f"[Error] Terjadi kesalahan saat menghapus: {e}")
