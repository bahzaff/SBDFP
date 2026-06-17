-- ==========================================
-- CHEAT SHEET / CONTEKAN DEMO DATABASE KOSKU
-- ==========================================

-- Pastikan selalu masuk ke database kosku terlebih dahulu!
USE kosku_db;

-- ---------------------------------------------------------
-- 1. QUERY CREATE (INSERT / TAMBAH DATA)
-- ---------------------------------------------------------
-- Menambahkan Penghuni Baru (Ganti angka 11 sesuai ID terakhir + 1)
INSERT INTO Penghuni (id_penghuni, nama_penghuni, jenis_kelamin, no_hp, email, alamat_asal)
VALUES (11, 'Joko Anwar', 'Laki-laki', '081234567890', 'joko@gmail.com', 'Jakarta');

-- ---------------------------------------------------------
-- 2. QUERY READ (SELECT / TAMPILKAN DATA)
-- ---------------------------------------------------------
-- Menampilkan semua daftar penghuni
SELECT * FROM Penghuni;

-- Menampilkan kamar yang saat ini 'Tersedia' (Kosong)
SELECT nomor_kamar, tipe_kamar, harga_sewa 
FROM Kamar 
WHERE status_kamar = 'Tersedia';

-- ---------------------------------------------------------
-- 3. QUERY UPDATE (UBAH DATA)
-- ---------------------------------------------------------
-- Mengubah (Update) status kamar B02 menjadi Terisi
UPDATE Kamar 
SET status_kamar = 'Terisi' 
WHERE nomor_kamar = 'B02';

-- Mengubah Nomor HP penghuni berdasarkan ID
UPDATE Penghuni 
SET no_hp = '089999999999' 
WHERE id_penghuni = 11;

-- ---------------------------------------------------------
-- 4. QUERY DELETE (HAPUS DATA)
-- ---------------------------------------------------------
-- Menghapus penghuni (Syarat: Pastikan penghuni ini belum punya Kontrak!)
DELETE FROM Penghuni 
WHERE id_penghuni = 11;

-- ---------------------------------------------------------
-- 5. SOAL JEBAKAN DOSEN: DDL (ALTER TABLE)
-- ---------------------------------------------------------
-- Menambahkan kolom 'pekerjaan' ke tabel Penghuni
ALTER TABLE Penghuni 
ADD pekerjaan VARCHAR(50);

-- Mengisi kolom pekerjaan yang baru saja dibuat
UPDATE Penghuni 
SET pekerjaan = 'Mahasiswa' 
WHERE id_penghuni = 1;
