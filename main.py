import sys
from controllers.setup_controller import setup_database
from controllers.mysql_controller import menu_cek_kamar_kosong, menu_cek_kontrak_hampir_habis, menu_rekap_tagihan_denda
from controllers.mongo_controller import menu_cari_review_mongodb
from controllers.chart_controller import menu_grafik_status_kamar, menu_grafik_distribusi_rating

# ==============================================================================
# PROGRAM UTAMA (CLI INTERAKTIF)
# ==============================================================================

def main():
    while True:
        print("\n" + "="*50)
        print("           SISTEM MANAJEMEN KOS (KOSKU)           ")
        print("="*50)
        print("0. Setup & Inisialisasi Database   ")
        print("-" * 50)
        print("1. Cek Kamar Kosong (MySQL)")
        print("2. Cek Kontrak Hampir Habis (MySQL)")
        print("3. Rekap Tagihan & Denda (MySQL JOIN)")
        print("4. Cari Review MongoDB (MongoDB)")
        print("5. Grafik Status Kamar (MySQL & Plotext)")
        print("6. Grafik Distribusi Rating (MongoDB & Plotext)")
        print("7. Keluar")
        print("="*50)
        
        pilihan = input("Pilih menu navigasi (0-7): ")
        
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
            print("Sistem ditutup. Terima kasih!")
            sys.exit(0)
        else:
            print("Pilihan menu tidak valid, silakan coba lagi.")

if __name__ == "__main__":
    main()
