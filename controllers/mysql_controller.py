from config.database import run_query_mysql

def menu_cek_kamar_kosong():
    """Menu 1: Cek Kamar Kosong (MySQL)"""
    print("\n--- DAFTAR KAMAR KOSONG ---")
    query = "SELECT nomor_kamar, tipe_kamar, harga_sewa, fasilitas FROM Kamar WHERE status_kamar = 'Tersedia'"
    
    data = run_query_mysql(query)
    if data is None: return
        
    if len(data) == 0:
        print("Semua kamar sedang penuh terisi.")
    else:
        for row in data:
            print(f"Kamar: {row['nomor_kamar']:<5} | Tipe: {row['tipe_kamar']:<10} | Harga: Rp {row['harga_sewa']:,.2f} | Fasilitas: {row['fasilitas']}")

def menu_cek_kontrak_hampir_habis():
    """Menu 2: Cek Kontrak Hampir Habis (MySQL)"""
    print("\n--- KONTRAK HAMPIR HABIS (Mendekati Tanggal Selesai) ---")
    query = """
        SELECT p.nama_penghuni, k.nomor_kamar, ko.tanggal_selesai, DATEDIFF(ko.tanggal_selesai, CURDATE()) as sisa_hari
        FROM Kontrak ko
        JOIN Penghuni p ON ko.id_penghuni = p.id_penghuni
        JOIN Kamar k ON ko.id_kamar = k.id_kamar
        WHERE DATEDIFF(ko.tanggal_selesai, CURDATE()) BETWEEN -30 AND 30
          AND ko.status_kontrak = 'Aktif'
        ORDER BY ko.tanggal_selesai ASC
    """
    
    data = run_query_mysql(query)
    if data is None: return
        
    if len(data) == 0:
        print("Tidak ada kontrak aktif yang hampir habis dalam waktu dekat.")
    else:
        for row in data:
            print(f"Penghuni: {row['nama_penghuni']} (Kamar {row['nomor_kamar']}) | Selesai: {row['tanggal_selesai']} (Sisa/Minus {row['sisa_hari']} hari)")

def menu_rekap_tagihan_denda():
    """Menu 3: Rekap Tagihan & Denda (MySQL Complex JOIN)"""
    print("\n--- REKAP TOTAL TAGIHAN & DENDA PENGHUNI ---")
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
    if not data: return
        
    for row in data:
        print(f"[{row['status_bayar'].upper()}] Penghuni: {row['nama_penghuni']} (Kamar {row['nomor_kamar']}) - Tagihan {row['bulan_tagihan']}")
        print(f"   Tagihan Pokok : Rp {row['tagihan_pokok']:,.2f}")
        print(f"   Total Denda   : Rp {row['total_denda']:,.2f}")
        print(f"   Total Bayar   : Rp {row['total_harus_dibayar']:,.2f}")
        print("-" * 60)

from datetime import datetime

def menu_kirim_notifikasi():
    """Portal Pemilik: Mengirim Notifikasi ke Penghuni"""
    print("\n--- KIRIM NOTIFIKASI KE PENGHUNI ---")
    id_input = input("Masukkan ID Penghuni tujuan: ")
    if not id_input.isdigit():
        print("[Error] ID Penghuni harus berupa angka bulat!")
        return
    id_penghuni = int(id_input)
    
    # Validasi ID
    cek = run_query_mysql("SELECT nama_penghuni FROM Penghuni WHERE id_penghuni = %s", (id_penghuni,))
    if not cek:
        print(f"[Error] Penghuni dengan ID {id_penghuni} tidak ditemukan!")
        return
        
    nama_tujuan = cek[0]['nama_penghuni']
    print(f"\nTujuan: {nama_tujuan}")
    print("Pilih Jenis Notifikasi:")
    print("1. Pengingat Pembayaran")
    print("2. Tagihan Belum Dibayar")
    print("3. Kontrak Akan Berakhir")
    print("4. Kontrak Berakhir")
    print("5. Pembayaran Berhasil")
    
    pilihan = input("Pilihan (1-5): ")
    jenis_map = {
        '1': 'Pengingat Pembayaran',
        '2': 'Tagihan Belum Dibayar',
        '3': 'Kontrak Akan Berakhir',
        '4': 'Kontrak Berakhir',
        '5': 'Pembayaran Berhasil'
    }
    
    if pilihan not in jenis_map:
        print("[Error] Pilihan jenis notifikasi tidak valid.")
        return
        
    jenis = jenis_map[pilihan]
    tgl_sekarang = datetime.now().strftime('%Y-%m-%d')
    
    # Generate ID Notifikasi
    max_id_query = run_query_mysql("SELECT MAX(id_notifikasi) as max_id FROM Notifikasi")
    new_id = (max_id_query[0]['max_id'] or 0) + 1
    
    # Insert
    query_insert = """
        INSERT INTO Notifikasi (id_notifikasi, id_penghuni, jenis_notifikasi, tanggal_notifikasi, status_baca)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        run_query_mysql(query_insert, (new_id, id_penghuni, jenis, tgl_sekarang, 'Belum Dibaca'), fetch=False)
        print(f"[Sukses] Notifikasi '{jenis}' berhasil dikirim ke {nama_tujuan}!")
    except Exception as e:
        print(f"[Error] Gagal mengirim notifikasi: {e}")

def menu_lihat_notifikasi():
    """Portal Penghuni: Melihat Kotak Masuk Notifikasi"""
    print("\n--- KOTAK MASUK NOTIFIKASI ---")
    id_input = input("Masukkan ID Penghuni Anda: ")
    if not id_input.isdigit():
        print("[Error] ID Penghuni harus berupa angka bulat!")
        return
    id_penghuni = int(id_input)
    
    query = """
        SELECT id_notifikasi, jenis_notifikasi, tanggal_notifikasi, status_baca 
        FROM Notifikasi 
        WHERE id_penghuni = %s 
        ORDER BY tanggal_notifikasi DESC, id_notifikasi DESC
    """
    data = run_query_mysql(query, (id_penghuni,))
    
    if not data:
        print("Tidak ada notifikasi untuk Anda.")
        return
        
    print("\nDaftar Notifikasi:")
    ada_belum_dibaca = False
    for idx, row in enumerate(data, 1):
        status = "[NEW]" if row['status_baca'] == 'Belum Dibaca' else "[READ]"
        if row['status_baca'] == 'Belum Dibaca':
            ada_belum_dibaca = True
        print(f"{idx}. {status} {row['tanggal_notifikasi']} - {row['jenis_notifikasi']}")
        
    if ada_belum_dibaca:
        tanya = input("\nTandai semua notifikasi sebagai 'Sudah Dibaca'? (y/n): ")
        if tanya.lower() == 'y':
            try:
                run_query_mysql("UPDATE Notifikasi SET status_baca = 'Sudah Dibaca' WHERE id_penghuni = %s", (id_penghuni,), fetch=False)
                print("[Sukses] Semua notifikasi telah ditandai sebagai sudah dibaca.")
            except Exception as e:
                print(f"[Error] Gagal mengubah status: {e}")
