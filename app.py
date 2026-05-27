from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from datetime import date
import json
import os

app = Flask(__name__)

# Data dummy untuk dashboard
DATAberandaAdmin = {
    "siswa": {
        "hadir": 32,
        "sakit": 1,
        "izin": 1,
        "total": 34
    },
    "kas": {
        "saldo": 103000,
        "pemasukan": 113000,
        "pengeluaran": 15000
    },
    "jadwal_pelajaran": [
        {"mapel": "DPK", "guru": "Pak Nutriyo", "jam": "jam ke 1 - 2"},
        {"mapel": "Seni Budaya", "guru": "Bu Vita", "jam": "jam ke 5 - 6"},
        {"mapel": "BK", "guru": "Bu Muza", "jam": "jam ke 7"},
        {"mapel": "Sejarah", "guru": "Pak Riza", "jam": "jam ke 3 - 4"},
        {"mapel": "PIPADS", "guru": "Bu Venis", "jam": "jam ke 8 - 10"},
    ],
    "piket_hari_ini": [
        "Haidar", "Eka", "Fatih", "Alin",
        "Dita", "Akbar", "Fajar", "Azzam"
    ],
    "pengumuman": [
        {"judul": "Sumatif Akhir Semester Genap", "oleh": "admin", "tanggal": "25 Mei s.d 9 Juni 2026"},
        {"judul": "Pembagian Rapor Semester Genap", "oleh": "admin", "tanggal": "19 Juni 2026"},
    ],
    "agenda": [
        {"tanggal": "25 Mei 2026", "kegiatan": "Presentasi proyek SAS kelas 10"},
        {"tanggal": "18 Juni 2026", "kegiatan": "Hari Ulang Tahun SMK Negeri 2 Singosari"},
    ]
}
@app.route("/")
def home():

    return render_template('login.html')

# Kode sekolah yang benar
KODE_SEKOLAH_BENAR = "INORASISMKN2SINGOSARI"

@app.route("/daftar", methods=["GET", "POST"])
def register():

    error = ""

    if request.method == "POST":

        kode_sekolah = request.form["kode_sekolah"]
        email = request.form["email"]
        password = request.form["password"]
        konfirmasi = request.form["konfirmasi"]
        username = request.form["username"]

        # VALIDASI KODE SEKOLAH
        if kode_sekolah != KODE_SEKOLAH_BENAR:
            error = "Kode sekolah salah!"

        # VALIDASI PASSWORD
        elif password != konfirmasi:
            error = "Password tidak sama!"

        else:
            error = "Registrasi berhasil!"

            print("Kode Sekolah :", kode_sekolah)
            print("Email :", email)
            print("Username :", username)

    return render_template("daftar.html", error=error)


@app.route("/beranda_admin")
def beranda():
    now = datetime.now()
    hari_ini = now.strftime("%A, %d %B %Y")
    return render_template("beranda_admin.html", data=DATAberandaAdmin, hari_ini=hari_ini)

app.secret_key = 'agenda-kelas-secret-key'

DATA_FILE = 'data_agenda.json'

# ===== MONTHS (untuk format tanggal) =====
BULAN = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
         'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
HARI  = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']

# ===== BACA / SIMPAN DATA =====
def baca_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def simpan_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def format_tanggal(tanggal_str):
    try:
        d = datetime.strptime(tanggal_str, '%Y-%m-%d')
        return f"{HARI[d.weekday()]}, {d.day} {BULAN[d.month]} {d.year}"
    except:
        return tanggal_str

# ===== BANGUN agenda_dict untuk kalender =====
# Format: { "2026-5-1": ["Agenda A", "Agenda B"], ... }
def build_agenda_dict(agenda_list):
    result = {}
    for item in agenda_list:
        try:
            d = datetime.strptime(item['tanggal'], '%Y-%m-%d')
            key = f"{d.year}-{d.month}-{d.day}"
            if key not in result:
                result[key] = []
            result[key].append(item['judul'])
        except:
            pass
    return result

# ===== HALAMAN 1 – KALENDER =====
@app.route('/agenda_admin')
def index():
    agenda_list = baca_data()
    agenda_dict = build_agenda_dict(agenda_list)
    return render_template('agenda_admin.html', agenda=agenda_dict)

# ===== HALAMAN 2 – FORM TAMBAH / KELOLA AGENDA =====
@app.route('/agenda_admin/kelola')
def agenda():
    agenda_list = baca_data()
    for item in agenda_list:
        item['tanggal_display'] = format_tanggal(item['tanggal'])
    today         = date.today().isoformat()
    # Tanggal bisa dikirim dari kalender via query param
    pre_tanggal   = request.args.get('tanggal', today)
    return render_template('tambahAgenda.html',
                           agenda_list=agenda_list,
                           today=today,
                           pre_tanggal=pre_tanggal)

# ===== TAMBAH AGENDA =====
@app.route('/agenda_admin/tambah', methods=['POST'])
def tambah():
    judul   = request.form.get('judul', '').strip()
    tanggal = request.form.get('tanggal', '').strip()
    catatan = request.form.get('catatan', '').strip()

    if not judul:
        flash('Judul agenda tidak boleh kosong!', 'error')
        return redirect(url_for('agenda'))
    if not tanggal:
        flash('Tanggal tidak boleh kosong!', 'error')
        return redirect(url_for('agenda'))

    agenda_list = baca_data()
    agenda_list.append({
        'id'     : len(agenda_list) + 1,
        'judul'  : judul,
        'tanggal': tanggal,
        'catatan': catatan
    })
    simpan_data(agenda_list)
    flash('Agenda berhasil ditambahkan!', 'success')
    return redirect(url_for('agenda'))

# ===== HAPUS AGENDA =====
@app.route('/agenda_admin/hapus/<int:index>', methods=['POST'])
def hapus(index):
    agenda_list = baca_data()
    if 0 <= index < len(agenda_list):
        agenda_list.pop(index)
        simpan_data(agenda_list)
        flash('Agenda berhasil dihapus!', 'success')
    return redirect(url_for('agenda'))

# ===== EDIT AGENDA =====
@app.route('/agenda_admin/edit/<int:index>', methods=['POST'])
def edit(index):
    judul   = request.form.get('judul', '').strip()
    tanggal = request.form.get('tanggal', '').strip()
    catatan = request.form.get('catatan', '').strip()

    if not judul:
        flash('Judul agenda tidak boleh kosong!', 'error')
        return redirect(url_for('agenda'))
    if not tanggal:
        flash('Tanggal tidak boleh kosong!', 'error')
        return redirect(url_for('agenda'))

    agenda_list = baca_data()
    if 0 <= index < len(agenda_list):
        agenda_list[index]['judul']   = judul
        agenda_list[index]['tanggal'] = tanggal
        agenda_list[index]['catatan'] = catatan
        simpan_data(agenda_list)
        flash('Agenda berhasil diperbarui!', 'success')
    return redirect(url_for('agenda'))

@app.route("/jadwalpiket_admin")
def jadwalpiket_admin():

    return render_template('jadwalpiket_admin.html')


jadwal = {
    "SENIN": [
        {"mapel": "DPK", "guru": "Pak Nutryo", "jam": "jam ke 1 - 2"},
        {"mapel": "Sejarah", "guru": "Pak Riza", "jam": "jam ke 3 - 4"},
    ],
    "SELASA": [
        {"mapel": "Informatika", "guru": "Bu Rere", "jam": "jam ke 1 - 4"},
        {"mapel": "PJOK", "guru": "Pak Agung", "jam": "jam ke 5 - 7"},
    ],
    "RABU": [
        {"mapel": "Matematika", "guru": "Bu Wiwin", "jam": "jam ke 1 - 4"},
    ],
    "KAMIS": [
        {"mapel": "Bahasa Inggris", "guru": "Bu Fajar", "jam": "jam ke 1 - 3"},
    ],
    "JUM'AT": [
        {"mapel": "Bahasa Indonesia", "guru": "Pak Taufik", "jam": "jam ke 3 - 5"},
    ],
}

hari_ini = {
    "hari": "SELASA",
    "pelajaran": [
        {"nama": "Informatika", "jam": "07.00 - 09.00"},
        {"nama": "PJOK",        "jam": "09.00 - 11.00"},
        {"nama": "PAI",         "jam": "11.00 - 13.00"},
    ]
}

urutan = ["SENIN", "SELASA", "RABU", "KAMIS", "JUM'AT"]

@app.route("/jadwalpelajaran_admin")
def jadwalpelajaran_admin():
    return render_template("jadwalpelajaran_admin.html", jadwal=jadwal, hari_ini=hari_ini, urutan=urutan)

@app.route("/pengumuman_admin")
def tambahpengumuman():
    return render_template("pengumuman_admin.html")

@app.route("/pengumuman_admin/tambah")
def pengumuman_admin():
    return render_template('tambahPengumuman.html')


if __name__ == "__main__":
    app.run(debug=True)