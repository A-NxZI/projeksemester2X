from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
import os
from datetime import date, datetime
from werkzeug.utils import secure_filename

agenda_bp = Blueprint('agenda', __name__)

DATA_FILE = 'data_agenda.json'
ALLOWED_EXT = {'jpg', 'jpeg'}
MAX_FILE_SIZE = 700 * 1024  # bytes

# ===== MONTHS =====
BULAN = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
         'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
HARI  = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']

# ===== HELPER: path folder uploads =====
def get_uploads_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')

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

# ===== HELPER: simpan file flyer ke disk =====
def simpan_flyer(file_obj):
    """
    Validasi dan simpan file flyer.
    Return: (filename_str, error_msg_str)
    - Sukses : (nama_file, None)
    - Gagal  : (None, pesan_error)
    """
    if not file_obj or not file_obj.filename:
        return None, None  # tidak ada file, bukan error

    filename = secure_filename(file_obj.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if ext not in ALLOWED_EXT:
        return None, 'Format flyer tidak didukung. Gunakan JPG/JPEG.'

    data = file_obj.read()
    if len(data) > MAX_FILE_SIZE:
        return None, f'Ukuran flyer melebihi batas 700 KB ({len(data)//1024} KB).'

    uploads_dir = get_uploads_dir()
    os.makedirs(uploads_dir, exist_ok=True)

    base = f"{int(datetime.now().timestamp())}_{filename}"
    with open(os.path.join(uploads_dir, base), 'wb') as f:
        f.write(data)

    return base, None

# ===== HELPER: hapus file flyer dari disk =====
def hapus_flyer(filename):
    if not filename:
        return
    try:
        path = os.path.join(get_uploads_dir(), filename)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

# ===== BANGUN agenda_dict untuk kalender =====
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
@agenda_bp.route('/agenda')
def index():
    agenda_list = baca_data()
    agenda_dict = build_agenda_dict(agenda_list)
    return render_template('agenda_admin.html', agenda=agenda_dict)

# ===== HALAMAN 2 – FORM TAMBAH / KELOLA AGENDA =====
@agenda_bp.route('/agenda/tambah')
def agenda():
    agenda_list = baca_data()
    for item in agenda_list:
        item['tanggal_display'] = format_tanggal(item['tanggal'])
        if 'flyer' not in item:
            item['flyer'] = ''
    today       = date.today().isoformat()
    pre_tanggal = request.args.get('tanggal', today)
    return render_template('agenda_tambah_admin.html',
                           agenda_list=agenda_list,
                           today=today,
                           pre_tanggal=pre_tanggal)

# ===== TAMBAH AGENDA =====
@agenda_bp.route('/agenda/tambah', methods=['POST'])
def tambah():
    judul   = request.form.get('judul', '').strip()
    tanggal = request.form.get('tanggal', '').strip()
    catatan = request.form.get('catatan', '').strip()

    if not judul:
        flash('Judul agenda tidak boleh kosong!', 'error')
        return redirect(url_for('agenda.agenda'))
    if not tanggal:
        flash('Tanggal tidak boleh kosong!', 'error')
        return redirect(url_for('agenda.agenda'))

    # Simpan flyer
    flyer_filename, err = simpan_flyer(request.files.get('flyer'))
    if err:
        flash(err, 'error')
        return redirect(url_for('agenda.agenda'))

    agenda_list = baca_data()
    agenda_list.append({
        'id'     : len(agenda_list) + 1,
        'judul'  : judul,
        'tanggal': tanggal,
        'catatan': catatan,
        'flyer'  : flyer_filename or ''
    })
    simpan_data(agenda_list)
    flash('Agenda berhasil ditambahkan!', 'success')
    return redirect(url_for('agenda.agenda'))

# ===== HAPUS AGENDA =====
@agenda_bp.route('/hapus/<int:index>', methods=['POST'])
def hapus(index):
    agenda_list = baca_data()
    if 0 <= index < len(agenda_list):
        item = agenda_list.pop(index)
        hapus_flyer(item.get('flyer'))
        simpan_data(agenda_list)
        flash('Agenda berhasil dihapus!', 'success')
    return redirect(url_for('agenda.agenda'))

# ===== EDIT AGENDA =====
@agenda_bp.route('/agenda/edit/<int:index>', methods=['POST'])
def edit(index):
    judul   = request.form.get('judul', '').strip()
    tanggal = request.form.get('tanggal', '').strip()
    catatan = request.form.get('catatan', '').strip()

    if not judul:
        flash('Judul agenda tidak boleh kosong!', 'error')
        return redirect(url_for('agenda.agenda'))
    if not tanggal:
        flash('Tanggal tidak boleh kosong!', 'error')
        return redirect(url_for('agenda.agenda'))

    agenda_list = baca_data()
    if 0 <= index < len(agenda_list):
        # Upload flyer baru (opsional)
        flyer_filename, err = simpan_flyer(request.files.get('flyer'))
        if err:
            flash(err, 'error')
            return redirect(url_for('agenda.agenda'))

        # Jika ada flyer baru, hapus yang lama
        if flyer_filename:
            hapus_flyer(agenda_list[index].get('flyer'))
            agenda_list[index]['flyer'] = flyer_filename

        agenda_list[index]['judul']   = judul
        agenda_list[index]['tanggal'] = tanggal
        agenda_list[index]['catatan'] = catatan
        simpan_data(agenda_list)
        flash('Agenda berhasil diperbarui!', 'success')

    return redirect(url_for('agenda.agenda'))
