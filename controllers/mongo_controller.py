import re
from config.database import get_mongo_connection

def menu_cari_review_mongodb():
    """Menu 4: Cari Review MongoDB (find() by tags/rating)"""
    print("\n--- PENCARIAN REVIEW MONGODB ---")
    kata_kunci = input("Masukkan keyword tag (contoh: bersih) atau tekan Enter untuk skip: ")
    rating_input = input("Masukkan minimal rating (1-5) atau tekan Enter untuk skip: ")
    
    mongo_db = get_mongo_connection()
    if mongo_db is None: return
        
    try:
        collection = mongo_db['reviews']
        query = {}
        
        if kata_kunci:
            regex_pattern = re.compile(f".*{kata_kunci}.*", re.IGNORECASE)
            query['tags'] = {"$in": [regex_pattern]}
            
        if rating_input.isdigit():
            query['rating'] = {"$gte": int(rating_input)}
            
        hasil_pencarian = collection.find(query)
        
        count = 0
        for review in hasil_pencarian:
            count += 1
            bintang = "★" * int(review.get('rating', 0))
            tags_str = ", ".join(review.get('tags', []))
            
            print(f"\n[{bintang}] Tags: {tags_str}")
            print(f"Review: \"{review.get('komentar')}\"")
            
            balasan = review.get('balasan_pemilik')
            if balasan:
                print(f"  -> Balasan Pemilik ({balasan.get('tanggal_balasan')}): {balasan.get('isi')}")
            else:
                print("  -> (Belum ada balasan dari pemilik)")
                
        if count == 0:
            print("Tidak ada review yang cocok dengan pencarian Anda.")
            
    except Exception as e:
        print(f"Terjadi error saat query MongoDB: {e}")

from config.database import run_query_mysql
from datetime import datetime

def menu_beri_review():
    """Portal Penghuni: Berikan/Ubah Review Kamar (MongoDB Upsert)"""
    print("\n" + "="*40)
    print("       PORTAL REVIEW PENGHUNI       ")
    print("="*40)
    
    # 1. Validasi Kepemilikan (Authentication)
    id_input = input("Masukkan ID Penghuni Anda: ")
    if not id_input.isdigit():
        print("[Error] ID Penghuni harus berupa angka bulat!")
        return
        
    id_penghuni = int(id_input)
    
    # Cek di database MySQL apakah penghuni ini punya riwayat sewa (Kontrak)
    query_cek = """
        SELECT k.id_kamar, k.nomor_kamar 
        FROM Kontrak ko 
        JOIN Kamar k ON ko.id_kamar = k.id_kamar 
        WHERE ko.id_penghuni = %s
    """
    riwayat_kamar = run_query_mysql(query_cek, (id_penghuni,))
    
    if not riwayat_kamar:
        print(f"[Akses Ditolak] Penghuni dengan ID {id_penghuni} tidak ditemukan atau belum pernah menyewa kamar!")
        return
        
    # Jika dia pernah nyewa beberapa kamar, suruh pilih
    print("\nKamar yang pernah/sedang Anda sewa:")
    kamar_valid_ids = []
    for r in riwayat_kamar:
        print(f"- Kamar {r['nomor_kamar']} (ID Kamar: {r['id_kamar']})")
        kamar_valid_ids.append(r['id_kamar'])
        
    kamar_input = input("\nMasukkan ID Kamar yang ingin Anda review: ")
    if not kamar_input.isdigit() or int(kamar_input) not in kamar_valid_ids:
        print("[Error] Anda hanya diizinkan me-review kamar yang pernah Anda sewa!")
        return
        
    id_kamar_pilihan = int(kamar_input)
    
    # 2. Ambil Input Review
    while True:
        rating_input = input("Berikan Rating (1-5): ")
        if rating_input.isdigit() and 1 <= int(rating_input) <= 5:
            rating = int(rating_input)
            break
        print("[Error] Rating harus berupa angka 1 sampai 5!")
        
    komentar = input("Ketikkan Ulasan / Komentar Anda: ")
    
    tags_input = input("Berikan kata kunci/tags (pisahkan dengan koma, cth: bersih,nyaman): ")
    tags = [t.strip() for t in tags_input.split(',')] if tags_input else []
    
    # 3. UPSERT ke MongoDB
    mongo_db = get_mongo_connection()
    if mongo_db is None: return
        
    try:
        collection = mongo_db['reviews']
        
        # Data yang akan di-set
        review_data = {
            "rating": rating,
            "komentar": komentar,
            "tags": tags,
            "tanggal_review": datetime.now().strftime('%Y-%m-%d')
        }
        
        # Logika Upsert: Cocokkan id_penghuni dan id_kamar
        filter_query = {"id_penghuni": id_penghuni, "id_kamar": id_kamar_pilihan}
        update_query = {"$set": review_data}
        
        # upsert=True berarti: Jika belum ada, Insert. Jika sudah ada, Update (Timpa).
        hasil = collection.update_one(filter_query, update_query, upsert=True)
        
        if hasil.upserted_id:
            print("\n[Sukses] Review BARU berhasil disimpan ke MongoDB! Terima kasih atas ulasan Anda.")
        else:
            print("\n[Sukses] Review LAMA Anda berhasil DITIMPA dengan ulasan baru!")
            
    except Exception as e:
        print(f"Terjadi error saat Upsert ke MongoDB: {e}")
