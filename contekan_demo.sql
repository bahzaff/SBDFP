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

-- ---------------------------------------------------------
-- 6. ADVANCED: JOIN (MENGGABUNGKAN TABEL)
-- ---------------------------------------------------------
-- INNER JOIN: Menampilkan Nama Penghuni dan Nomor Kamar yang sedang mereka sewa
-- [PENJELASAN]: INNER JOIN mensyaratkan data harus punya pasangan di semua tabel. 
-- Kalau ada orang belum nyewa kamar, atau kamar yg kosong, datanya akan terbuang/disembunyikan!
SELECT p.nama_penghuni, k.nomor_kamar, ko.status_kontrak
FROM Penghuni p
JOIN Kontrak ko ON p.id_penghuni = ko.id_penghuni
JOIN Kamar k ON ko.id_kamar = k.id_kamar
WHERE ko.status_kontrak = 'Aktif';

-- LEFT JOIN: Menampilkan semua kamar, beserta nama penghuninya JIKA ada (kalau kosong akan NULL)
-- [PENJELASAN]: LEFT JOIN memprioritaskan tabel Kiri (Kamar). Semua isi tabel Kamar pasti dimunculkan.
-- Jika tabel Kanan (Penghuni) kosong, maka akan ditulis NULL, tapi data Kamar-nya TIDAK akan dibuang.
SELECT k.nomor_kamar, p.nama_penghuni
FROM Kamar k
LEFT JOIN Kontrak ko ON k.id_kamar = ko.id_kamar AND ko.status_kontrak = 'Aktif'
LEFT JOIN Penghuni p ON ko.id_penghuni = p.id_penghuni;

-- ---------------------------------------------------------
-- 7. ADVANCED: AGGREGATION & GROUP BY
-- ---------------------------------------------------------
-- Menghitung jumlah kamar per tipe kamar
-- [PENJELASAN]: GROUP BY akan mengelompokkan data yang kembar (Standard/Deluxe) jadi 1 baris,
-- lalu COUNT(*) bertugas menghitung ada berapa jumlah data di masing-masing kelompok itu.
SELECT tipe_kamar, COUNT(*) AS jumlah_kamar 
FROM Kamar 
GROUP BY tipe_kamar;

-- Menghitung total tagihan masuk yang sudah LUNAS
-- [PENJELASAN]: SUM bertugas menjumlahkan isi angka dari kolom (seperti auto-sum di Excel).
SELECT SUM(jumlah_bayar) AS total_pendapatan 
FROM Pembayaran 
WHERE status_bayar = 'Lunas';

-- ---------------------------------------------------------
-- 8. ADVANCED: SUBQUERY (QUERY DI DALAM QUERY)
-- ---------------------------------------------------------
-- Mencari penghuni yang membayar tagihan paling mahal
-- [PENJELASAN]: Query Bersarang! Sistem mengeksekusi kurung paling dalam dulu (SELECT MAX), 
-- misal hasilnya 1.500.000. Lalu query di luarnya akan mencari siapa yang bayar senilai itu.
SELECT nama_penghuni FROM Penghuni 
WHERE id_penghuni IN (
    SELECT ko.id_penghuni FROM Kontrak ko 
    JOIN Pembayaran pb ON ko.id_kontrak = pb.id_kontrak 
    WHERE pb.jumlah_bayar = (SELECT MAX(jumlah_bayar) FROM Pembayaran)
);

-- ---------------------------------------------------------
-- 9. ADVANCED: VIEW (MEMBUAT TABEL VIRTUAL / SHORTCUT)
-- ---------------------------------------------------------
-- Membuat VIEW untuk melihat daftar tagihan agar tidak perlu ngetik JOIN panjang-panjang lagi
-- [PENJELASAN]: Daripada ngetik ulang JOIN 4 tabel tiap hari, kita bungkus query panjang ini 
-- menjadi sebuah "Tabel Virtual" bernama view_daftar_tagihan sebagai shortcut.
CREATE VIEW view_daftar_tagihan AS
SELECT p.nama_penghuni, k.nomor_kamar, pb.jumlah_bayar, pb.status_bayar
FROM Penghuni p
JOIN Kontrak ko ON p.id_penghuni = ko.id_penghuni
JOIN Kamar k ON ko.id_kamar = k.id_kamar
JOIN Pembayaran pb ON ko.id_kontrak = pb.id_kontrak;

-- Cara memanggil View di atas:
-- SELECT * FROM view_daftar_tagihan;

-- ---------------------------------------------------------
-- 10. ADVANCED: TRIGGER (OTOMATISASI DATABASE)
-- ---------------------------------------------------------
-- Mengubah Delimiter agar MySQL tidak bingung membaca tanda titik koma (;) di dalam blok Trigger
DELIMITER //

-- Membuat Trigger: "Setiap ada pembayaran berstatus 'Lunas', 
-- pastikan status kontraknya diubah menjadi 'Aktif'"
-- [PENJELASAN]: Ini adalah robot otomasi di dalam DB. AFTER UPDATE berarti dia mengintai 
-- kapan ada data di-update. IF NEW... berarti dia ngecek apakah status barunya jadi Lunas.
-- Kalau iya, robot ini langsung meng-Update tabel Kontrak jadi Aktif secara otomatis!
CREATE TRIGGER trigger_bayar_lunas
AFTER UPDATE ON Pembayaran
FOR EACH ROW
BEGIN
    IF NEW.status_bayar = 'Lunas' AND OLD.status_bayar != 'Lunas' THEN
        UPDATE Kontrak 
        SET status_kontrak = 'Aktif' 
        WHERE id_kontrak = NEW.id_kontrak;
    END IF;
END //

DELIMITER ;
-- Peringatan Demo: Cara mengetes trigger ini adalah dengan menjalankan perintah UPDATE 
-- pada tabel pembayaran untuk mengubah status_bayar dari Belum Lunas menjadi Lunas.

-- [LANGKAH DEMO TEST TRIGGER]
-- 1. Tunjukkan dulu bahwa ada pembayaran ID 4 (Kontrak 2) yang belum lunas
SELECT * FROM Pembayaran WHERE id_pembayaran = 4;

-- 2. Tunjukkan status Kontrak 2 saat ini
SELECT id_kontrak, status_kontrak FROM Kontrak WHERE id_kontrak = 2;

-- 3. Eksekusi UPDATE (pura-puranya si penghuni baru saja bayar)
UPDATE Pembayaran 
SET status_bayar = 'Lunas' 
WHERE id_pembayaran = 4;

-- 4. Panggil lagi tabel Kontrak, BOOM! Status kontraknya pasti otomatis berubah jadi 'Aktif'!
SELECT id_kontrak, status_kontrak FROM Kontrak WHERE id_kontrak = 2;
