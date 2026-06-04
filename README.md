# SiNilai — Sistem Informasi Nilai Siswa
# SMA XYZ | Tugas 2 — Implementasi Sistem

## Teknologi
- Backend  : Python 3 + Flask
- Frontend : HTML5 + CSS3 + JavaScript (Vanilla)
- Database : MySQL
- Library  : mysql-connector-python

---

## Cara Instalasi & Menjalankan

### 1. Install dependensi Python
```bash
pip install -r requirements.txt
```

### 2. Setup Database MySQL
Buka MySQL client (XAMPP / MySQL Workbench / Terminal), lalu jalankan:
```bash
mysql -u root -p < setup_db.sql
```
Atau copy-paste isi `setup_db.sql` ke MySQL Workbench dan eksekusi.

### 3. Sesuaikan konfigurasi database
Buka `app.py`, cari bagian `DB_CONFIG`, sesuaikan password MySQL Anda:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'PASSWORD_MYSQL_ANDA',  # <- ubah ini
    'database': 'sinilai_db',
}
```

### 4. Jalankan aplikasi
```bash
python app.py
```
Buka browser: http://localhost:5000

---

## Akun Default (Password: password123)

| Username    | Password    | Peran  | Keterangan              |
|-------------|-------------|--------|-------------------------|
| admin       | password123 | Admin  | Akses penuh             |
| guru_budi   | password123 | Guru   | Mapel: Matematika       |
| guru_siti   | password123 | Guru   | Mapel: Bahasa Indonesia |
| guru_andi   | password123 | Guru   | Mapel: Fisika           |
| siswa_001   | password123 | Siswa  | Ahmad Fauzi – X-A       |
| siswa_002   | password123 | Siswa  | Dewi Lestari – X-A      |
| siswa_003   | password123 | Siswa  | Rizky Ramadhan – X-B    |

---

## Struktur Direktori
```
sinilai/
├── app.py              ← Aplikasi utama (Flask + OOP + Terstruktur)
├── setup_db.sql        ← Script SQL untuk buat database & seed data
├── requirements.txt    ← Dependensi Python
├── static/
│   ├── css/style.css   ← Stylesheet (Dark Academic Theme)
│   └── js/main.js      ← JavaScript (kalkulator, interaksi)
└── templates/
    ├── base.html        ← Layout utama (sidebar + topbar)
    ├── login.html       ← Halaman login
    ├── dashboard.html   ← Dashboard (Admin/Guru/Siswa)
    ├── siswa.html       ← Daftar siswa (Admin)
    ├── form_siswa.html  ← Form tambah/edit siswa
    ├── guru.html        ← Daftar guru (Admin)
    ├── form_guru.html   ← Form tambah/edit guru
    ├── input_nilai.html ← Input nilai (Guru)
    ├── validasi_nilai.html ← Validasi nilai (Guru)
    ├── nilai_siswa.html ← Lihat nilai pribadi (Siswa)
    ├── kelola_nilai.html ← Kelola nilai (Admin)
    └── laporan.html     ← Laporan nilai (Admin/Guru)
```

---

## Rumus Nilai Akhir
```
NA = (30% × Tugas) + (30% × UTS) + (40% × UAS)
Status Lulus: NA >= 70
```

## Hak Akses
- Admin  : CRUD siswa, guru, nilai; laporan semua siswa
- Guru   : Input nilai, validasi, rekap nilai mapelnya
- Siswa  : Read-only nilai pribadi & status kelulusan
