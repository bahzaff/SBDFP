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
        print("3. Selesaikan Kontrak Penghuni (UPDATE)")
        print("4. Bersihkan Notifikasi Lama (DELETE)")
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
                    
                    # 6. Fitur Pembayaran Tagihan Pertama
                    harga_kamar = kamar_valid['harga_sewa']
                    print(f"\n--- PEMBAYARAN TAGIHAN PERTAMA ---")
                    print(f"Total Tagihan Bulan Pertama: Rp {harga_kamar:,.0f}")
                    
                    while True:
                        uang_input = input("Masukkan jumlah uang yang dibayarkan sekarang (Rp): ")
                        if uang_input.isdigit() and int(uang_input) >= 0:
                            uang_dibayar = int(uang_input)
                            break
                        print("[Error] Masukkan nominal uang yang valid!")
                        
                    if uang_dibayar >= harga_kamar:
                        status_bayar = 'Lunas'
                        uang_dibayar = harga_kamar # Normalisasi jika bayar lebih
                        print("=> Status Pembayaran: LUNAS")
                    else:
                        status_bayar = 'Belum Lunas'
                        print(f"=> Status Pembayaran: BELUM LUNAS (Hanya DP, Kurang Rp {harga_kamar - uang_dibayar:,.0f})")
                        
                    # Generate ID Pembayaran & Insert
                    max_pb = run_query_mysql("SELECT MAX(id_pembayaran) as max_id FROM Pembayaran")
                    new_id_pb = (max_pb[0]['max_id'] or 0) + 1 if max_pb else 1
                    
                    bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                    nama_bulan = f"{bulan_indo[tgl_mulai.month - 1]} {tgl_mulai.year}"
                    tgl_jatuh_tempo = tgl_mulai + timedelta(days=7)
                    
                    q_pb = """
                        INSERT INTO Pembayaran (id_pembayaran, id_kontrak, bulan_tagihan, tanggal_jatuh_tempo, tanggal_bayar, jumlah_bayar, status_bayar)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    p_pb = (new_id_pb, new_id_kontrak, nama_bulan, tgl_jatuh_tempo.strftime('%Y-%m-%d'), tgl_mulai.strftime('%Y-%m-%d'), uang_dibayar, status_bayar)
                    run_query_mysql(q_pb, p_pb, fetch=False)
                    
                    print(f"\n[Sukses Luar Biasa] Penghuni '{nama}' resmi menempati Kamar '{kamar_valid['nomor_kamar']}' selama {durasi_bulan} Bulan ke depan dan Tagihan Pertama berhasil dicatat!")
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
    print("\n--- SELESAIKAN KONTRAK PENGHUNI (UPDATE) ---")
    _read_penghuni() # Tampilkan data agar user bisa melihat ID-nya
    
    try:
        print("\nMasukkan ID Penghuni yang akan diselesaikan kontraknya...")
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
            print(f"[Info] Penghuni ID {id_penghuni} saat ini tidak memiliki kamar / kontrak aktif yang bisa di-checkout.")
            return
            
        print(f"\n[PERINGATAN] Proses ini akan mengakhiri kontrak penghuni dan mengubah status kamar menjadi 'Tersedia'.")
        print("Data riwayat pembayaran dan penghuni TETAP AMAN (Tidak Dihapus dari Database).")
        konfirmasi = input(f"Yakin memproses Checkout Penghuni ID {id_penghuni}? (y/n): ")
        
        if konfirmasi.lower() == 'y':
            # 1. Update Kontrak jadi Selesai
            run_query_mysql("UPDATE Kontrak SET status_kontrak = 'Selesai' WHERE id_penghuni = %s AND status_kontrak = 'Aktif'", (id_penghuni,), fetch=False)
            
            # 2. Update status semua kamar yang disewa penghuni tersebut jadi Tersedia
            for k in kontrak_aktif:
                run_query_mysql("UPDATE Kamar SET status_kamar = 'Tersedia' WHERE id_kamar = %s", (k['id_kamar'],), fetch=False)
                
            print(f"[Sukses] Proses Checkout ID {id_penghuni} berhasil! Kamar telah dibebaskan.")
        else:
            print("Dibatalkan.")
    except Exception as e:
        print(f"[Error] Terjadi kesalahan saat memproses checkout: {e}")

def _delete_penghuni():
    print("\n--- BERSIHKAN KOTAK MASUK NOTIFIKASI (DELETE) ---")
    _read_penghuni()
    
    try:
        print("\nMasukkan ID Penghuni yang ingin dibersihkan notifikasinya...")
        id_input = input("ID: ")
        if not id_input.isdigit():
            print("[Error] Input ID harus berupa angka bulat!")
            return
        id_penghuni = int(id_input)
        
        # Cek notifikasi yang sudah dibaca
        q_notif = "SELECT * FROM Notifikasi WHERE id_penghuni = %s AND status_baca = 'Sudah Dibaca'"
        notif_lama = run_query_mysql(q_notif, (id_penghuni,))
        
        if not notif_lama:
            print(f"[Info] Penghuni ID {id_penghuni} tidak memiliki notifikasi lama ('Sudah Dibaca') yang bisa dihapus.")
            return
            
        print(f"\nDitemukan {len(notif_lama)} notifikasi lama untuk Penghuni ID {id_penghuni}.")
        for n in notif_lama:
            print(f"- {n['tanggal_notifikasi']} | {n['jenis_notifikasi']}")
            
        konfirmasi = input(f"\nYakin menghapus secara permanen {len(notif_lama)} notifikasi ini? (y/n): ")
        
        if konfirmasi.lower() == 'y':
            # Eksekusi Hard Delete murni
            run_query_mysql("DELETE FROM Notifikasi WHERE id_penghuni = %s AND status_baca = 'Sudah Dibaca'", (id_penghuni,), fetch=False)
            print(f"[Sukses] Proses Delete Murni berhasil! Notifikasi lama telah lenyap dari database.")
        else:
            print("Dibatalkan.")
    except Exception as e:
        print(f"[Error] Terjadi kesalahan saat menghapus: {e}")
