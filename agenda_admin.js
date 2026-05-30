// --------------------------------------------------
// DATA
// --------------------------------------------------
const MONTHS_ID = [
  "Januari","Februari","Maret","April","Mei","Juni",
  "Juli","Agustus","September","Oktober","November","Desember"
];

const YEAR = 2026;

// --------------------------------------------------
// STATE
// --------------------------------------------------
let currentMonth = new Date().getMonth(); // bulan saat ini secara default
let selectedCell = null;

// --------------------------------------------------
// HELPERS
// --------------------------------------------------
function buildKey(year, month, day) {
  return `${year}-${month + 1}-${day}`;
}
// new helper untuk cek apakah tanggal sudah lewat atau belum
function isPastDate(isoDate) {
  const today = new Date();
  today.setHours(0, 0, 0, 0); // reset jam ke awal hari
  const target = new Date(isoDate);
  return target < today;
}

// Format tanggal ke string ISO (YYYY-MM-DD) untuk dikirim ke halaman agenda
function toISO(year, month, day) {
  const mm = String(month + 1).padStart(2, '0');
  const dd = String(day).padStart(2, '0');
  return `${year}-${mm}-${dd}`;
}

// --------------------------------------------------
// RENDER CALENDAR
// --------------------------------------------------
function renderCalendar() {
  document.getElementById("calTitle").textContent =
    `${MONTHS_ID[currentMonth]} ${YEAR}`;

  document.getElementById("prevBtn").disabled = currentMonth <= 0;
  document.getElementById("nextBtn").disabled = currentMonth >= 11;

  const grid    = document.getElementById("calGrid");
  const headers = Array.from(grid.children).slice(0, 7);
  grid.innerHTML = "";
  headers.forEach(h => grid.appendChild(h));

  const today       = new Date();
  const firstDayDOW = new Date(YEAR, currentMonth, 1).getDay();
  const daysInMonth = new Date(YEAR, currentMonth + 1, 0).getDate();
  const daysInPrev  = new Date(YEAR, currentMonth, 0).getDate();

  // Leading cells
  for (let i = 0; i < firstDayDOW; i++) {
    const day = daysInPrev - firstDayDOW + 1 + i;
    grid.appendChild(makeCell(day, currentMonth - 1, true));
  }

  // Current-month cells
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday =
      today.getFullYear() === YEAR &&
      today.getMonth()    === currentMonth &&
      today.getDate()     === d;
    grid.appendChild(makeCell(d, currentMonth, false, isToday));
  }

  // Trailing cells
  const trailingCount = (firstDayDOW + daysInMonth) % 7;
  const trailing      = trailingCount === 0 ? 0 : 7 - trailingCount;
  for (let d = 1; d <= trailing; d++) {
    grid.appendChild(makeCell(d, currentMonth + 1, true));
  }

  // Update agenda count
  let count = 0;
  Object.keys(agendaData).forEach(k => {
    const [y, m] = k.split("-").map(Number);
    if (y === YEAR && m === currentMonth + 1) {
      count += agendaData[k].length;
    }
  });
  document.getElementById("agendaCount").textContent =
    count > 0
      ? `${count} agenda dijadwalkan`
      : "Tidak ada agenda bulan ini";
}

// --------------------------------------------------
// BUILD A DAY CELL
// --------------------------------------------------
function makeCell(day, month, isOther, isToday = false) {
  const cell = document.createElement("div");
  cell.className = "day-cell";

  const dow = new Date(YEAR, month, day).getDay();
  if (isOther)                cell.classList.add("other-month");
  if (dow === 0 || dow === 6) cell.classList.add("weekend");
  if (isToday && !isOther)    cell.classList.add("today");

  const numEl = document.createElement("div");
  numEl.className   = "day-num";
  numEl.textContent = day;
  cell.appendChild(numEl);

  if (!isOther) {
    const k         = buildKey(YEAR, month, day);
    const hasAgenda = agendaData[k] && agendaData[k].length > 0;

    if (hasAgenda) {
      cell.classList.add("has-agenda");
      const dot = document.createElement("div");
      dot.className = "dot";
      cell.appendChild(dot);
    }

    cell.addEventListener("click", () => {
      if (selectedCell) selectedCell.classList.remove("selected");
      cell.classList.add("selected");
      selectedCell = cell;

      const isoDate = toISO(YEAR, month, day);
      const label   = `${day} ${MONTHS_ID[currentMonth]} ${YEAR}`;

      if (hasAgenda) {
        showModal(label, agendaData[k], isoDate);
      } else {
        showEmptyModal(label, isoDate);
      }
    });
  }

  return cell;
}

// --------------------------------------------------
// MODAL HELPERS
// --------------------------------------------------
function showModal(dateLabel, items, isoDate) {
  document.getElementById("modalDate").textContent  = dateLabel;
  document.getElementById("modalTitle").textContent = "Daftar Agenda";

  const list = document.getElementById("modalList");
  list.innerHTML = "";
  items.forEach(item => {
    const el = document.createElement("div");
    el.className   = "modal-agenda-item";
    el.textContent = item;
    list.appendChild(el);
  });

  // Set link tombol Tambah Agenda dengan tanggal yang dipilih
  document.getElementById("modalAddBtn").href = `/agenda/tambah?tanggal=${isoDate}`;

  document.getElementById("modalOverlay").classList.add("open");


 //  Sembunyikan tombol jika tanggal sudah lewat
  document.getElementById("modalAddBtn").style.display =
    isPastDate(isoDate) ? "none" : "";

  document.getElementById("modalOverlay").classList.add("open");
}

function showEmptyModal(dateLabel, isoDate) {
  document.getElementById("modalDate").textContent  = dateLabel;
  document.getElementById("modalTitle").textContent = "Belum Ada Agenda";
  document.getElementById("modalList").innerHTML    =
    `<div class="modal-empty">Tidak ada agenda untuk tanggal ini.</div>`;

  // Set link tombol Tambah Agenda dengan tanggal yang dipilih
  document.getElementById("modalAddBtn").href = `/agenda/tambah?tanggal=${isoDate}`;

  document.getElementById("modalOverlay").classList.add("open");
 //  Sembunyikan tombol jika tanggal sudah lewat
  document.getElementById("modalAddBtn").style.display =
    isPastDate(isoDate) ? "none" : "";

  document.getElementById("modalOverlay").classList.add("open");
}

function hideModal() {
  document.getElementById("modalOverlay").classList.remove("open");
  if (selectedCell) {
    selectedCell.classList.remove("selected");
    selectedCell = null;
  }
}

function closeModal(e) {
  if (e.target === document.getElementById("modalOverlay")) hideModal();
}

// --------------------------------------------------
// NAVIGATION
// --------------------------------------------------
function changeMonth(dir) {
  const next = currentMonth + dir;
  if (next < 0 || next > 11) return;
  currentMonth = next;
  renderCalendar();
}

// --------------------------------------------------
// INIT
// --------------------------------------------------
renderCalendar();
