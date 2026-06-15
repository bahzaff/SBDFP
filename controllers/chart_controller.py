import plotext as plt
from config.database import run_query_mysql, get_mongo_connection

def menu_grafik_status_kamar():
    """Menu 5: Grafik Status Kamar (Plotext & MySQL)"""
    print("\n--- GRAFIK STATUS KAMAR ---")
    query = "SELECT status_kamar, COUNT(*) as jumlah FROM Kamar GROUP BY status_kamar"
    data = run_query_mysql(query)
    
    if not data:
        print("Data kamar tidak ditemukan.")
        return
        
    labels = []
    values = []
    for row in data:
        labels.append(row['status_kamar'])
        values.append(row['jumlah'])
        
    if not values: return
        
    plt.clear_data()
    plt.bar(labels, values, color="cyan", marker="sd")
    plt.title("Grafik Jumlah Kamar Berdasarkan Status (MySQL)")
    plt.xlabel("Status Kamar")
    plt.ylabel("Jumlah Kamar")
    plt.theme("dark")
    plt.show()

def menu_grafik_distribusi_rating():
    """Menu 6: Grafik Distribusi Rating (Plotext & MongoDB)"""
    print("\n--- GRAFIK DISTRIBUSI RATING ---")
    mongo_db = get_mongo_connection()
    if mongo_db is None: return
        
    try:
        collection = mongo_db['reviews']
        
        pipeline = [
            {"$group": {"_id": "$rating", "jumlah": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        
        hasil = list(collection.aggregate(pipeline))
        
        if not hasil:
            print("Data review kosong.")
            return
            
        labels = []
        values = []
        for doc in hasil:
            labels.append(f"Bintang {doc['_id']}")
            values.append(doc['jumlah'])
            
        plt.clear_data()
        plt.bar(labels, values, color="green", marker="sd")
        plt.title("Grafik Distribusi Rating Penghuni (MongoDB)")
        plt.xlabel("Rating (Bintang)")
        plt.ylabel("Jumlah Review")
        plt.theme("dark")
        plt.show()
        
    except Exception as e:
        print(f"Terjadi error saat meload grafik MongoDB: {e}")
