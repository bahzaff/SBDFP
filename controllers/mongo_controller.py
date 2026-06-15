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
