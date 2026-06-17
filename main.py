import sys
from controllers.setup_controller import setup_database
from controllers.mysql_controller import menu_cek_kamar_kosong, menu_cek_kontrak_hampir_habis, menu_rekap_tagihan_denda, menu_kirim_notifikasi, menu_lihat_notifikasi
from controllers.mongo_controller import menu_cari_review_mongodb, menu_beri_review
from controllers.chart_controller import menu_grafik_status_kamar, menu_grafik_distribusi_rating
from controllers.crud_controller import menu_crud_penghuni

# ==============================================================================
# PROGRAM UTAMA (CLI INTERAKTIF)
# ==============================================================================

def menu_pemilik():
    while True:
        print("\n" + "="*50)
        print("         PORTAL PEMILIK KOS (DASHBOARD)           ")
        print("="*50)
        print("0. Setup & Inisialisasi Database   ")
        print("-" * 50)
        print("1. Cek Kamar Kosong (MySQL)")
        print("2. Cek Kontrak Hampir Habis (MySQL)")
        print("3. Rekap Tagihan & Denda (MySQL JOIN)")
        print("4. Cari Review MongoDB (MongoDB)")
        print("5. Grafik Status Kamar (MySQL & Plotext)")
        print("6. Grafik Distribusi Rating (MongoDB & Plotext)")
        print("7. Kelola Data Penghuni (CRUD Manual MySQL)")
        print("8. Kirim Notifikasi ke Penghuni (MySQL)")
        print("9. Kembali ke Gerbang Utama")
        print("="*50)
        
        pilihan = input("Pilih menu navigasi (0-9): ")
        
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
            menu_crud_penghuni()
        elif pilihan == '8':
            menu_kirim_notifikasi()
        elif pilihan == '9':
            break
        else:
            print("Pilihan menu tidak valid, silakan coba lagi.")

def menu_penghuni():
    while True:
        print("\n" + "="*50)
        print("        PORTAL PENGHUNI & PUBLIK KOSKU            ")
        print("="*50)
        print("1. Lihat Review & Ulasan Kamar (MongoDB)")
        print("2. Berikan/Ubah Review Kamar (Khusus Penghuni)")
        print("3. Lihat Kotak Masuk Notifikasi (MySQL)")
        print("0. Kembali ke Gerbang Utama")
        print("="*50)
        
        pilihan = input("Pilih menu navigasi (0-3): ")
        if pilihan == '1':
            menu_cari_review_mongodb()
        elif pilihan == '2':
            menu_beri_review()
        elif pilihan == '3':
            menu_lihat_notifikasi()
        elif pilihan == '0':
            break
        else:
            print("Pilihan menu tidak valid, silakan coba lagi.")

def main():
    while True:
        print("\n" + "="*50)
        print("       SELAMAT DATANG DI SISTEM MANAJEMEN KOS     ")
        print("="*50)
        print("1. Masuk sebagai Pemilik Kos")
        print("2. Masuk sebagai Penghuni/Publik")
        print("0. Keluar Aplikasi")
        print("="*50)
        
        pilihan = input("Pilih role Anda (0-2): ")
        if pilihan == '1':
            menu_pemilik()
        elif pilihan == '2':
            menu_penghuni()
        elif pilihan == '0':
            print("Sistem ditutup. Terima kasih!")
            sys.exit(0)
        else:
            print("Pilihan tidak valid, silakan coba lagi.")

if __name__ == "__main__":
    main()
