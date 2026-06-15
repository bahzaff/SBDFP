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
        WHERE DATEDIFF(ko.tanggal_selesai, CURDATE()) BETWEEN -30 AND 90
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
