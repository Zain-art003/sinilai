from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sinilai_sma_xyz_secret_key_2024'

# =============================================
# KONFIGURASI DATABASE
# =============================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Sesuaikan dengan password MySQL Anda
    'database': 'sinilai_db',
    'charset': 'utf8mb4'
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error koneksi database: {e}")
        return None

# =============================================
# PEMROGRAMAN TERSTRUKTUR (Min. 3 Fungsi)
# =============================================

def validasi_nilai(nilai):
    """Fungsi 1: Validasi nilai harus berada dalam rentang 0-100"""
    try:
        nilai = float(nilai)
        return 0 <= nilai <= 100
    except (ValueError, TypeError):
        return False

def hitung_nilai_akhir(nilai_tugas, nilai_uts, nilai_uas):
    """Fungsi 2: Hitung nilai akhir dengan bobot 30% Tugas + 30% UTS + 40% UAS"""
    return round((0.30 * float(nilai_tugas)) + (0.30 * float(nilai_uts)) + (0.40 * float(nilai_uas)), 2)

def tentukan_kelulusan(nilai_akhir):
    """Fungsi 3: Tentukan status kelulusan berdasarkan nilai akhir"""
    return 'LULUS' if float(nilai_akhir) >= 70 else 'TIDAK LULUS'

def hash_password(password):
    """Fungsi utilitas: Hash password menggunakan SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# =============================================
# CLASS OOP - SISWA
# =============================================
class Siswa:
    def __init__(self, id_siswa, nis, nama_siswa, kelas, id_user=None):
        self.id_siswa = id_siswa
        self.nis = nis
        self.nama = nama_siswa
        self.kelas = kelas
        self.id_user = id_user

    def get_info(self):
        return f"NIS: {self.nis} | Nama: {self.nama} | Kelas: {self.kelas}"

    def lihat_nilai(self, db_conn):
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT n.*, g.nama_guru FROM nilai n
            LEFT JOIN guru g ON n.id_guru = g.id_guru
            WHERE n.id_siswa = %s ORDER BY n.created_at DESC
        """, (self.id_siswa,))
        return cursor.fetchall()

    def lihat_status_kelulusan(self, db_conn):
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT mata_pelajaran, nilai_akhir, status_lulus
            FROM nilai WHERE id_siswa = %s
        """, (self.id_siswa,))
        return cursor.fetchall()

    def set_kelas(self, kelas_baru, db_conn):
        self.kelas = kelas_baru
        cursor = db_conn.cursor()
        cursor.execute("UPDATE siswa SET kelas = %s WHERE id_siswa = %s", (kelas_baru, self.id_siswa))
        db_conn.commit()

    def tampil_profil(self):
        return {'nis': self.nis, 'nama': self.nama, 'kelas': self.kelas}


# =============================================
# CLASS OOP - GURU
# =============================================
class Guru:
    def __init__(self, id_guru, id_guru_kode, nama_guru, mata_pelajaran, id_user=None):
        self.id_guru = id_guru
        self.id_guru_kode = id_guru_kode
        self.nama_guru = nama_guru
        self.mata_pelajaran = mata_pelajaran
        self.id_user = id_user

    def get_info(self):
        return f"ID: {self.id_guru_kode} | Nama: {self.nama_guru} | Mapel: {self.mata_pelajaran}"

    def input_nilai(self, siswa_obj, t, uts, uas, db_conn):
        """Method: Input nilai siswa dengan validasi"""
        if not (validasi_nilai(t) and validasi_nilai(uts) and validasi_nilai(uas)):
            return False, "Nilai harus berada dalam rentang 0-100"
        
        na = hitung_nilai_akhir(t, uts, uas)
        status = tentukan_kelulusan(na)
        
        cursor = db_conn.cursor()
        # Cek apakah sudah ada nilai untuk mata pelajaran ini
        cursor.execute("""
            SELECT id_nilai FROM nilai 
            WHERE id_siswa = %s AND mata_pelajaran = %s AND id_guru = %s
        """, (siswa_obj.id_siswa, self.mata_pelajaran, self.id_guru))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE nilai SET nilai_tugas=%s, nilai_uts=%s, nilai_uas=%s,
                nilai_akhir=%s, status_lulus=%s WHERE id_nilai=%s
            """, (t, uts, uas, na, status, existing[0]))
        else:
            cursor.execute("""
                INSERT INTO nilai (id_siswa, id_guru, mata_pelajaran, nilai_tugas, nilai_uts, nilai_uas, nilai_akhir, status_lulus)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (siswa_obj.id_siswa, self.id_guru, self.mata_pelajaran, t, uts, uas, na, status))
        
        db_conn.commit()
        return True, "Nilai berhasil disimpan"

    def validasi_nilai(self, nilai_obj):
        """Method: Validasi objek nilai"""
        return validasi_nilai(nilai_obj.get('nilai_tugas', -1)) and \
               validasi_nilai(nilai_obj.get('nilai_uts', -1)) and \
               validasi_nilai(nilai_obj.get('nilai_uas', -1))


# =============================================
# DECORATOR LOGIN REQUIRED
# =============================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('peran') not in roles:
                flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


# =============================================
# ROUTES - AUTH
# =============================================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username dan password wajib diisi.', 'danger')
            return render_template('login.html')
        
        conn = get_db()
        if not conn:
            flash('Gagal koneksi ke database.', 'danger')
            return render_template('login.html')
        
        cursor = conn.cursor(dictionary=True)
        hashed = hash_password(password)
        cursor.execute("""
            SELECT * FROM users WHERE username=%s AND password=%s AND aktif=1
        """, (username, hashed))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id_user']
            session['username'] = user['username']
            session['peran'] = user['peran']
            flash(f'Selamat datang, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah, atau akun tidak aktif.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('login'))


# =============================================
# ROUTES - DASHBOARD
# =============================================
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    stats = {}
    
    if session['peran'] == 'Admin':
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM siswa")
        stats['total_siswa'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM guru")
        stats['total_guru'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM nilai")
        stats['total_nilai'] = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM nilai WHERE status_lulus='LULUS'")
        stats['total_lulus'] = cursor.fetchone()['total']
        
    elif session['peran'] == 'Guru':
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_guru, nama_guru, mata_pelajaran FROM guru WHERE id_user=%s", (session['user_id'],))
        guru_data = cursor.fetchone()
        stats['guru'] = guru_data
        if guru_data:
            cursor.execute("SELECT COUNT(*) as total FROM nilai WHERE id_guru=%s", (guru_data['id_guru'],))
            stats['total_nilai_input'] = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) as total FROM nilai WHERE id_guru=%s AND status_lulus='LULUS'", (guru_data['id_guru'],))
            stats['total_lulus'] = cursor.fetchone()['total']
    
    elif session['peran'] == 'Siswa':
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM siswa WHERE id_user=%s", (session['user_id'],))
        siswa_data = cursor.fetchone()
        stats['siswa'] = siswa_data
        if siswa_data:
            cursor.execute("SELECT * FROM nilai WHERE id_siswa=%s", (siswa_data['id_siswa'],))
            nilai_list = cursor.fetchall()
            stats['nilai_list'] = nilai_list
            total_mapel = len(nilai_list)
            stats['total_mapel'] = total_mapel
            if total_mapel > 0:
                total_lulus = sum(1 for nilai in nilai_list if nilai.get('status_lulus') == 'LULUS')
                stats['total_lulus'] = total_lulus
                stats['total_tidak_lulus'] = total_mapel - total_lulus
                stats['rata_rata_nilai'] = round(sum(float(nilai.get('nilai_akhir', 0)) for nilai in nilai_list) / total_mapel, 2)
            else:
                stats['total_lulus'] = 0
                stats['total_tidak_lulus'] = 0
                stats['rata_rata_nilai'] = 0.0
    
    conn.close()
    return render_template('dashboard.html', stats=stats)


# =============================================
# ROUTES - ADMIN: KELOLA SISWA (CRUD)
# =============================================
@app.route('/siswa')
@login_required
@role_required('Admin')
def kelola_siswa():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT s.*, u.username FROM siswa s LEFT JOIN users u ON s.id_user=u.id_user ORDER BY s.nama_siswa")
    siswa_list = cursor.fetchall()
    conn.close()
    return render_template('siswa.html', siswa_list=siswa_list)

@app.route('/siswa/tambah', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def tambah_siswa():
    if request.method == 'POST':
        nis = request.form.get('nis', '').strip()
        nama = request.form.get('nama_siswa', '').strip()
        kelas = request.form.get('kelas', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not all([nis, nama, kelas, username, password]):
            flash('Semua field wajib diisi.', 'danger')
            return render_template('form_siswa.html', action='tambah')
        
        conn = get_db()
        cursor = conn.cursor()
        try:
            hashed = hash_password(password)
            cursor.execute("INSERT INTO users (username, password, peran) VALUES (%s, %s, 'Siswa')", (username, hashed))
            id_user = cursor.lastrowid
            cursor.execute("INSERT INTO siswa (nis, nama_siswa, kelas, id_user) VALUES (%s, %s, %s, %s)", (nis, nama, kelas, id_user))
            conn.commit()
            flash(f'Siswa {nama} berhasil ditambahkan.', 'success')
            return redirect(url_for('kelola_siswa'))
        except Error as e:
            conn.rollback()
            flash(f'Gagal menambahkan siswa: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('form_siswa.html', action='tambah', data=None)

@app.route('/siswa/edit/<int:id_siswa>', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def edit_siswa(id_siswa):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT s.*, u.username FROM siswa s JOIN users u ON s.id_user=u.id_user WHERE s.id_siswa=%s", (id_siswa,))
    siswa = cursor.fetchone()
    
    if not siswa:
        flash('Siswa tidak ditemukan.', 'danger')
        return redirect(url_for('kelola_siswa'))
    
    if request.method == 'POST':
        nis = request.form.get('nis', '').strip()
        nama = request.form.get('nama_siswa', '').strip()
        kelas = request.form.get('kelas', '').strip()
        password = request.form.get('password', '').strip()
        
        try:
            cursor.execute("UPDATE siswa SET nis=%s, nama_siswa=%s, kelas=%s WHERE id_siswa=%s", (nis, nama, kelas, id_siswa))
            if password:
                hashed = hash_password(password)
                cursor.execute("UPDATE users SET password=%s WHERE id_user=%s", (hashed, siswa['id_user']))
            conn.commit()
            flash(f'Data siswa {nama} berhasil diperbarui.', 'success')
            return redirect(url_for('kelola_siswa'))
        except Error as e:
            conn.rollback()
            flash(f'Gagal memperbarui data: {e}', 'danger')
        finally:
            conn.close()
    
    conn.close()
    return render_template('form_siswa.html', action='edit', data=siswa)

@app.route('/siswa/hapus/<int:id_siswa>', methods=['POST'])
@login_required
@role_required('Admin')
def hapus_siswa(id_siswa):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT s.*, s.id_user FROM siswa s WHERE id_siswa=%s", (id_siswa,))
    siswa = cursor.fetchone()
    if siswa:
        try:
            cursor.execute("DELETE FROM nilai WHERE id_siswa=%s", (id_siswa,))
            cursor.execute("DELETE FROM siswa WHERE id_siswa=%s", (id_siswa,))
            cursor.execute("DELETE FROM users WHERE id_user=%s", (siswa['id_user'],))
            conn.commit()
            flash('Siswa berhasil dihapus.', 'success')
        except Error as e:
            conn.rollback()
            flash(f'Gagal menghapus: {e}', 'danger')
    conn.close()
    return redirect(url_for('kelola_siswa'))


# =============================================
# ROUTES - ADMIN: KELOLA GURU (CRUD)
# =============================================
@app.route('/guru')
@login_required
@role_required('Admin')
def kelola_guru():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT g.*, u.username FROM guru g LEFT JOIN users u ON g.id_user=u.id_user ORDER BY g.nama_guru")
    guru_list = cursor.fetchall()
    conn.close()
    return render_template('guru.html', guru_list=guru_list)

@app.route('/guru/tambah', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def tambah_guru():
    if request.method == 'POST':
        id_guru_kode = request.form.get('id_guru_kode', '').strip()
        nama_guru = request.form.get('nama_guru', '').strip()
        mata_pelajaran = request.form.get('mata_pelajaran', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not all([id_guru_kode, nama_guru, mata_pelajaran, username, password]):
            flash('Semua field wajib diisi.', 'danger')
            return render_template('form_guru.html', action='tambah')
        
        conn = get_db()
        cursor = conn.cursor()
        try:
            hashed = hash_password(password)
            cursor.execute("INSERT INTO users (username, password, peran) VALUES (%s, %s, 'Guru')", (username, hashed))
            id_user = cursor.lastrowid
            cursor.execute("INSERT INTO guru (id_guru_kode, nama_guru, mata_pelajaran, id_user) VALUES (%s, %s, %s, %s)",
                           (id_guru_kode, nama_guru, mata_pelajaran, id_user))
            conn.commit()
            flash(f'Guru {nama_guru} berhasil ditambahkan.', 'success')
            return redirect(url_for('kelola_guru'))
        except Error as e:
            conn.rollback()
            flash(f'Gagal menambahkan guru: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('form_guru.html', action='tambah', data=None)

@app.route('/guru/edit/<int:id_guru>', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def edit_guru(id_guru):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT g.*, u.username FROM guru g JOIN users u ON g.id_user=u.id_user WHERE g.id_guru=%s", (id_guru,))
    guru = cursor.fetchone()
    
    if not guru:
        flash('Guru tidak ditemukan.', 'danger')
        return redirect(url_for('kelola_guru'))
    
    if request.method == 'POST':
        id_guru_kode = request.form.get('id_guru_kode', '').strip()
        nama_guru = request.form.get('nama_guru', '').strip()
        mata_pelajaran = request.form.get('mata_pelajaran', '').strip()
        password = request.form.get('password', '').strip()
        
        try:
            cursor.execute("UPDATE guru SET id_guru_kode=%s, nama_guru=%s, mata_pelajaran=%s WHERE id_guru=%s",
                           (id_guru_kode, nama_guru, mata_pelajaran, id_guru))
            if password:
                cursor.execute("UPDATE users SET password=%s WHERE id_user=%s", (hash_password(password), guru['id_user']))
            conn.commit()
            flash(f'Data guru {nama_guru} berhasil diperbarui.', 'success')
            return redirect(url_for('kelola_guru'))
        except Error as e:
            conn.rollback()
            flash(f'Gagal memperbarui: {e}', 'danger')
        finally:
            conn.close()
    
    conn.close()
    return render_template('form_guru.html', action='edit', data=guru)

@app.route('/guru/hapus/<int:id_guru>', methods=['POST'])
@login_required
@role_required('Admin')
def hapus_guru(id_guru):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_user FROM guru WHERE id_guru=%s", (id_guru,))
    guru = cursor.fetchone()
    if guru:
        try:
            cursor.execute("DELETE FROM nilai WHERE id_guru=%s", (id_guru,))
            cursor.execute("DELETE FROM guru WHERE id_guru=%s", (id_guru,))
            cursor.execute("DELETE FROM users WHERE id_user=%s", (guru['id_user'],))
            conn.commit()
            flash('Guru berhasil dihapus.', 'success')
        except Error as e:
            conn.rollback()
            flash(f'Gagal menghapus: {e}', 'danger')
    conn.close()
    return redirect(url_for('kelola_guru'))


# =============================================
# ROUTES - GURU: INPUT NILAI
# =============================================
@app.route('/nilai/input', methods=['GET', 'POST'])
@login_required
@role_required('Guru')
def input_nilai():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM guru WHERE id_user=%s", (session['user_id'],))
    guru_data = cursor.fetchone()
    
    if not guru_data:
        flash('Data guru tidak ditemukan.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))
    
    guru_obj = Guru(guru_data['id_guru'], guru_data['id_guru_kode'], guru_data['nama_guru'], guru_data['mata_pelajaran'], guru_data['id_user'])
    
    cursor.execute("SELECT id_siswa, nis, nama_siswa, kelas FROM siswa ORDER BY nama_siswa")
    siswa_list = cursor.fetchall()
    
    if request.method == 'POST':
        id_siswa = request.form.get('id_siswa')
        t = request.form.get('nilai_tugas')
        uts = request.form.get('nilai_uts')
        uas = request.form.get('nilai_uas')
        
        cursor.execute("SELECT * FROM siswa WHERE id_siswa=%s", (id_siswa,))
        s = cursor.fetchone()
        if not s:
            flash('Siswa tidak ditemukan.', 'danger')
        else:
            siswa_obj = Siswa(s['id_siswa'], s['nis'], s['nama_siswa'], s['kelas'], s['id_user'])
            ok, msg = guru_obj.input_nilai(siswa_obj, t, uts, uas, conn)
            if ok:
                flash(msg, 'success')
            else:
                flash(msg, 'danger')
        conn.close()
        return redirect(url_for('input_nilai'))
    
    # Rekap nilai yang sudah diinput guru ini
    cursor.execute("""
        SELECT n.*, s.nama_siswa, s.nis, s.kelas
        FROM nilai n JOIN siswa s ON n.id_siswa=s.id_siswa
        WHERE n.id_guru=%s ORDER BY n.created_at DESC
    """, (guru_data['id_guru'],))
    rekap_nilai = cursor.fetchall()
    conn.close()
    
    return render_template('input_nilai.html', guru=guru_data, siswa_list=siswa_list, rekap_nilai=rekap_nilai)

@app.route('/nilai/validasi')
@login_required
@role_required('Guru')
def validasi_nilai_guru():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM guru WHERE id_user=%s", (session['user_id'],))
    guru_data = cursor.fetchone()
    
    cursor.execute("""
        SELECT n.*, s.nama_siswa, s.nis, s.kelas
        FROM nilai n JOIN siswa s ON n.id_siswa=s.id_siswa
        WHERE n.id_guru=%s ORDER BY s.nama_siswa
    """, (guru_data['id_guru'],))
    nilai_list = cursor.fetchall()
    conn.close()
    return render_template('validasi_nilai.html', nilai_list=nilai_list, guru=guru_data)


# =============================================
# ROUTES - SISWA: LIHAT NILAI
# =============================================
@app.route('/nilai/saya')
@login_required
@role_required('Siswa')
def nilai_saya():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM siswa WHERE id_user=%s", (session['user_id'],))
    siswa_data = cursor.fetchone()
    
    nilai_list = []
    if siswa_data:
        siswa_obj = Siswa(siswa_data['id_siswa'], siswa_data['nis'], siswa_data['nama_siswa'], siswa_data['kelas'])
        nilai_list = siswa_obj.lihat_nilai(conn)
    
    conn.close()
    return render_template('nilai_siswa.html', siswa=siswa_data, nilai_list=nilai_list)


# =============================================
# ROUTES - LAPORAN (Admin & Guru)
# =============================================
@app.route('/laporan')
@login_required
@role_required('Admin', 'Guru')
def laporan():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    kelas_filter = request.args.get('kelas', '')
    mapel_filter = request.args.get('mata_pelajaran', '')
    status_filter = request.args.get('status', '')
    
    query = """
        SELECT n.*, s.nama_siswa, s.nis, s.kelas, g.nama_guru
        FROM nilai n
        JOIN siswa s ON n.id_siswa=s.id_siswa
        JOIN guru g ON n.id_guru=g.id_guru
        WHERE 1=1
    """
    params = []
    
    if session['peran'] == 'Guru':
        cursor.execute("SELECT id_guru FROM guru WHERE id_user=%s", (session['user_id'],))
        guru = cursor.fetchone()
        if guru:
            query += " AND n.id_guru=%s"
            params.append(guru['id_guru'])
    
    if kelas_filter:
        query += " AND s.kelas=%s"
        params.append(kelas_filter)
    if mapel_filter:
        query += " AND n.mata_pelajaran=%s"
        params.append(mapel_filter)
    if status_filter:
        query += " AND n.status_lulus=%s"
        params.append(status_filter)
    
    query += " ORDER BY s.kelas, s.nama_siswa"
    cursor.execute(query, params)
    laporan_data = cursor.fetchall()
    
    # Ambil daftar kelas dan mapel untuk filter
    cursor.execute("SELECT DISTINCT kelas FROM siswa ORDER BY kelas")
    kelas_list = [r['kelas'] for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT mata_pelajaran FROM nilai ORDER BY mata_pelajaran")
    mapel_list = [r['mata_pelajaran'] for r in cursor.fetchall()]
    
    conn.close()
    return render_template('laporan.html', laporan_data=laporan_data,
                           kelas_list=kelas_list, mapel_list=mapel_list,
                           kelas_filter=kelas_filter, mapel_filter=mapel_filter, status_filter=status_filter)


# =============================================
# ROUTES - KELOLA NILAI (Admin)
# =============================================
@app.route('/nilai/kelola')
@login_required
@role_required('Admin')
def kelola_nilai():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT n.*, s.nama_siswa, s.nis, s.kelas, g.nama_guru
        FROM nilai n
        JOIN siswa s ON n.id_siswa=s.id_siswa
        JOIN guru g ON n.id_guru=g.id_guru
        ORDER BY n.created_at DESC
    """)
    nilai_list = cursor.fetchall()
    conn.close()
    return render_template('kelola_nilai.html', nilai_list=nilai_list)

@app.route('/nilai/hapus/<int:id_nilai>', methods=['POST'])
@login_required
@role_required('Admin')
def hapus_nilai(id_nilai):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM nilai WHERE id_nilai=%s", (id_nilai,))
    conn.commit()
    conn.close()
    flash('Data nilai berhasil dihapus.', 'success')
    return redirect(url_for('kelola_nilai'))


# =============================================
# API: Kalkulasi Real-time
# =============================================
@app.route('/api/hitung', methods=['POST'])
@login_required
def api_hitung():
    data = request.get_json()
    t = data.get('tugas', 0)
    uts = data.get('uts', 0)
    uas = data.get('uas', 0)
    
    if not (validasi_nilai(t) and validasi_nilai(uts) and validasi_nilai(uas)):
        return jsonify({'error': 'Nilai harus antara 0-100'}), 400
    
    na = hitung_nilai_akhir(t, uts, uas)
    status = tentukan_kelulusan(na)
    return jsonify({'nilai_akhir': na, 'status': status})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
