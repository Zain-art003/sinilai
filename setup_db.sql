-- =============================================
-- SETUP DATABASE: sinilai_db
-- SMA XYZ - Sistem Informasi Nilai Siswa
-- =============================================

CREATE DATABASE IF NOT EXISTS sinilai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sinilai_db;

-- Tabel Users (Login)
CREATE TABLE IF NOT EXISTS users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    peran ENUM('Admin', 'Guru', 'Siswa') NOT NULL,
    aktif TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabel Siswa
CREATE TABLE IF NOT EXISTS siswa (
    id_siswa INT AUTO_INCREMENT PRIMARY KEY,
    nis VARCHAR(20) NOT NULL UNIQUE,
    nama_siswa VARCHAR(100) NOT NULL,
    kelas VARCHAR(20) NOT NULL,
    id_user INT,
    FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE SET NULL
);

-- Tabel Guru
CREATE TABLE IF NOT EXISTS guru (
    id_guru INT AUTO_INCREMENT PRIMARY KEY,
    id_guru_kode VARCHAR(20) NOT NULL UNIQUE,
    nama_guru VARCHAR(100) NOT NULL,
    mata_pelajaran VARCHAR(100) NOT NULL,
    id_user INT,
    FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE SET NULL
);

-- Tabel Nilai
CREATE TABLE IF NOT EXISTS nilai (
    id_nilai INT AUTO_INCREMENT PRIMARY KEY,
    id_siswa INT NOT NULL,
    id_guru INT NOT NULL,
    mata_pelajaran VARCHAR(100) NOT NULL,
    nilai_tugas FLOAT NOT NULL,
    nilai_uts FLOAT NOT NULL,
    nilai_uas FLOAT NOT NULL,
    nilai_akhir FLOAT NOT NULL,
    status_lulus ENUM('LULUS', 'TIDAK LULUS') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_siswa) REFERENCES siswa(id_siswa) ON DELETE CASCADE,
    FOREIGN KEY (id_guru) REFERENCES guru(id_guru) ON DELETE CASCADE
);

-- =============================================
-- DATA AWAL (SEED)
-- Password semua akun: "password123" (SHA-256)
-- SHA256("password123") = ef92b778bafe771207b6e4c4a25d4a9a7f0e57...
-- =============================================

-- Admin
INSERT INTO users (username, password, peran) VALUES
('admin', SHA2('password123', 256), 'Admin');

-- Guru
INSERT INTO users (username, password, peran) VALUES
('guru_budi', SHA2('password123', 256), 'Guru'),
('guru_siti', SHA2('password123', 256), 'Guru'),
('guru_andi', SHA2('password123', 256), 'Guru');

-- Siswa
INSERT INTO users (username, password, peran) VALUES
('siswa_001', SHA2('password123', 256), 'Siswa'),
('siswa_002', SHA2('password123', 256), 'Siswa'),
('siswa_003', SHA2('password123', 256), 'Siswa'),
('siswa_004', SHA2('password123', 256), 'Siswa'),
('siswa_005', SHA2('password123', 256), 'Siswa');

-- Data Guru
INSERT INTO guru (id_guru_kode, nama_guru, mata_pelajaran, id_user) VALUES
('GR001', 'Budi Santoso', 'Matematika', (SELECT id_user FROM users WHERE username='guru_budi')),
('GR002', 'Siti Rahayu', 'Bahasa Indonesia', (SELECT id_user FROM users WHERE username='guru_siti')),
('GR003', 'Andi Pratama', 'Fisika', (SELECT id_user FROM users WHERE username='guru_andi'));

-- Data Siswa
INSERT INTO siswa (nis, nama_siswa, kelas, id_user) VALUES
('2024001', 'Ahmad Fauzi', 'X-A', (SELECT id_user FROM users WHERE username='siswa_001')),
('2024002', 'Dewi Lestari', 'X-A', (SELECT id_user FROM users WHERE username='siswa_002')),
('2024003', 'Rizky Ramadhan', 'X-B', (SELECT id_user FROM users WHERE username='siswa_003')),
('2024004', 'Nur Aini', 'X-B', (SELECT id_user FROM users WHERE username='siswa_004')),
('2024005', 'Farhan Maulana', 'XI-A', (SELECT id_user FROM users WHERE username='siswa_005'));

-- Data Nilai Contoh
INSERT INTO nilai (id_siswa, id_guru, mata_pelajaran, nilai_tugas, nilai_uts, nilai_uas, nilai_akhir, status_lulus) VALUES
(1, 1, 'Matematika', 85, 78, 90, 84.7, 'LULUS'),
(2, 1, 'Matematika', 70, 65, 60, 64.5, 'TIDAK LULUS'),
(3, 1, 'Matematika', 90, 88, 92, 90.2, 'LULUS'),
(4, 1, 'Matematika', 75, 72, 80, 76.1, 'LULUS'),
(5, 1, 'Matematika', 60, 55, 58, 57.7, 'TIDAK LULUS'),
(1, 2, 'Bahasa Indonesia', 88, 82, 85, 84.9, 'LULUS'),
(2, 2, 'Bahasa Indonesia', 92, 90, 95, 92.6, 'LULUS'),
(3, 3, 'Fisika', 78, 80, 75, 77.4, 'LULUS'),
(4, 3, 'Fisika', 65, 60, 55, 59.5, 'TIDAK LULUS');
